"""
BigQuery Data Loader - Load Synthea healthcare data from BigQuery into PySpark
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from typing import Optional, Dict, List
import yaml
from pathlib import Path


class BigQueryLoader:
    """
    Load healthcare data from BigQuery public datasets into PySpark DataFrames.
    
    Supports:
    - CMS Synthetic Patient Data (OMOP format)
    - Streaming and batch loading
    - Automatic schema inference
    - Partitioning and filtering
    
    Example:
        >>> loader = BigQueryLoader(spark)
        >>> patients_df = loader.load_patients(limit=10000)
        >>> encounters_df = loader.load_encounters(start_date="2020-01-01")
    """
    
    def __init__(
        self, 
        spark: SparkSession,
        gcp_project: Optional[str] = None
    ):
        """
        Initialize BigQuery loader.
        
        Args:
            spark: Active SparkSession
            gcp_project: GCP project ID for billing
        """
        self.spark = spark
        self.gcp_project = gcp_project or self._load_project_id()
        
        # BigQuery public dataset
        self.source_project = "bigquery-public-data"
        self.source_dataset = "cms_synthetic_patient_data_omop"
        
        print(f"✅ BigQueryLoader initialized")
        print(f"   Billing Project: {self.gcp_project}")
        print(f"   Source Dataset: {self.source_project}.{self.source_dataset}")
    
    def _load_project_id(self) -> str:
        """Load GCP project ID from config."""
        config_path = Path(__file__).parent.parent.parent / "config" / "gcp_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config["project"]["id"]
    
    def _read_table(
        self,
        table_name: str,
        filter_query: Optional[str] = None,
        limit: Optional[int] = None
    ) -> DataFrame:
        """
        Read table from BigQuery into Spark DataFrame.
        
        Args:
            table_name: BigQuery table name
            filter_query: SQL WHERE clause (without WHERE keyword)
            limit: Maximum number of rows
            
        Returns:
            Spark DataFrame
        """
        full_table = f"{self.source_project}.{self.source_dataset}.{table_name}"
        
        # Build query
        query = f"SELECT * FROM `{full_table}`"
        if filter_query:
            query += f" WHERE {filter_query}"
        if limit:
            query += f" LIMIT {limit}"
        
        print(f"🔍 Loading: {table_name} (query: {len(query)} chars)")
        
        # Read from BigQuery using Spark-BigQuery connector
        df = self.spark.read \
            .format("bigquery") \
            .option("project", self.gcp_project) \
            .option("query", query) \
            .load()
        
        row_count = df.count()
        print(f"✅ Loaded {row_count:,} rows from {table_name}")
        
        return df
    
    def load_patients(
        self,
        limit: Optional[int] = None,
        min_birth_year: Optional[int] = None
    ) -> DataFrame:
        """
        Load patient demographics data.
        
        Schema:
        - person_id: Patient identifier
        - gender_concept_id: Gender code
        - year_of_birth: Birth year
        - race_concept_id: Race code
        - ethnicity_concept_id: Ethnicity code
        
        Args:
            limit: Max number of patients
            min_birth_year: Filter patients born after this year
            
        Returns:
            Patients DataFrame
        """
        filter_query = None
        if min_birth_year:
            filter_query = f"EXTRACT(YEAR FROM birth_datetime) >= {min_birth_year}"
        
        df = self._read_table("person", filter_query, limit)
        
        # Add age calculation
        df = df.withColumn(
            "age",
            F.year(F.current_date()) - F.year(F.col("birth_datetime"))
        )
        
        return df
    
    def load_encounters(
        self,
        limit: Optional[int] = None,
        start_date: Optional[str] = None
    ) -> DataFrame:
        """
        Load hospital encounters (visits).
        
        Schema:
        - visit_occurrence_id: Encounter identifier
        - person_id: Patient identifier
        - visit_start_date: Admission date
        - visit_end_date: Discharge date
        - visit_type_concept_id: Visit type (ER, inpatient, outpatient)
        
        Args:
            limit: Max number of encounters
            start_date: Filter encounters after this date (YYYY-MM-DD)
            
        Returns:
            Encounters DataFrame
        """
        filter_query = None
        if start_date:
            filter_query = f"visit_start_date >= '{start_date}'"
        
        df = self._read_table("visit_occurrence", filter_query, limit)
        
        # Calculate length of stay
        df = df.withColumn(
            "length_of_stay_days",
            F.datediff(F.col("visit_end_date"), F.col("visit_start_date"))
        )
        
        return df
    
    def load_conditions(
        self,
        limit: Optional[int] = None,
        concept_ids: Optional[List[int]] = None
    ) -> DataFrame:
        """
        Load patient conditions (diagnoses).
        
        Schema:
        - condition_occurrence_id: Record identifier
        - person_id: Patient identifier
        - condition_concept_id: Diagnosis code (SNOMED)
        - condition_start_date: Diagnosis date
        
        Args:
            limit: Max number of records
            concept_ids: Filter by specific diagnosis codes
            
        Returns:
            Conditions DataFrame
        """
        filter_query = None
        if concept_ids:
            ids_str = ",".join(map(str, concept_ids))
            filter_query = f"condition_concept_id IN ({ids_str})"
        
        return self._read_table("condition_occurrence", filter_query, limit)
    
    def load_procedures(
        self,
        limit: Optional[int] = None
    ) -> DataFrame:
        """
        Load procedures performed on patients.
        
        Returns:
            Procedures DataFrame
        """
        return self._read_table("procedure_occurrence", limit=limit)
    
    def load_medications(
        self,
        limit: Optional[int] = None
    ) -> DataFrame:
        """
        Load medication prescriptions.
        
        Returns:
            Medications DataFrame
        """
        return self._read_table("drug_exposure", limit=limit)
    
    def load_observations(
        self,
        limit: Optional[int] = None
    ) -> DataFrame:
        """
        Load lab results and vital signs.
        
        Returns:
            Observations DataFrame
        """
        return self._read_table("observation", limit=limit)
    
    def load_all_tables(
        self,
        limit: Optional[int] = 1000
    ) -> Dict[str, DataFrame]:
        """
        Load all main tables into a dictionary.
        
        Args:
            limit: Max rows per table
            
        Returns:
            Dictionary mapping table names to DataFrames
        """
        print(f"📦 Loading all tables (limit={limit} per table)...\n")
        
        tables = {
            "patients": self.load_patients(limit),
            "encounters": self.load_encounters(limit),
            "conditions": self.load_conditions(limit),
            "procedures": self.load_procedures(limit),
            "medications": self.load_medications(limit),
            "observations": self.load_observations(limit)
        }
        
        print(f"\n✅ All tables loaded:")
        for name, df in tables.items():
            print(f"   {name}: {df.count():,} rows")
        
        return tables


# Example usage
if __name__ == "__main__":
    from ..utils.spark_session import get_spark_session
    
    # Create Spark session
    spark = get_spark_session(app_name="BigQueryLoader_Test")
    
    # Initialize loader
    loader = BigQueryLoader(spark, gcp_project="your-project-id")
    
    # Load sample data
    print("\n" + "="*60)
    print("Loading patients...")
    patients_df = loader.load_patients(limit=100)
    patients_df.show(5)
    patients_df.printSchema()
    
    print("\n" + "="*60)
    print("Loading encounters...")
    encounters_df = loader.load_encounters(limit=100)
    encounters_df.show(5)
    
    # Stop Spark
    spark.stop()
