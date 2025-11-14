"""
PySpark Data Cleaning and Transformation
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType, DateType
from typing import List, Optional


class DataCleaner:
    """
    Clean and prepare healthcare data for analysis.
    
    Features:
    - Remove duplicates
    - Handle missing values
    - Standardize data types
    - Filter invalid records
    - Add derived columns
    """
    
    def __init__(self, df: DataFrame):
        """
        Initialize cleaner with DataFrame.
        
        Args:
            df: Input Spark DataFrame
        """
        self.df = df
        self.original_count = df.count()
        print(f"📊 DataCleaner initialized: {self.original_count:,} rows")
    
    def remove_duplicates(self, subset: Optional[List[str]] = None) -> 'DataCleaner':
        """
        Remove duplicate rows.
        
        Args:
            subset: Columns to consider for duplicates. If None, uses all columns.
            
        Returns:
            Self for method chaining
        """
        before = self.df.count()
        self.df = self.df.dropDuplicates(subset=subset)
        after = self.df.count()
        
        removed = before - after
        print(f"🔧 Removed {removed:,} duplicate rows ({removed/before*100:.1f}%)")
        
        return self
    
    def handle_missing_values(
        self,
        strategy: str = "drop",
        subset: Optional[List[str]] = None,
        fill_value: Optional[any] = None
    ) -> 'DataCleaner':
        """
        Handle missing values.
        
        Args:
            strategy: "drop" or "fill"
            subset: Columns to consider
            fill_value: Value to fill (if strategy="fill")
            
        Returns:
            Self for method chaining
        """
        before = self.df.count()
        
        if strategy == "drop":
            self.df = self.df.dropna(subset=subset)
        elif strategy == "fill":
            self.df = self.df.fillna(fill_value, subset=subset)
        
        after = self.df.count()
        removed = before - after
        
        print(f"🔧 Handled missing values: {removed:,} rows affected")
        
        return self
    
    def filter_invalid_dates(
        self,
        date_column: str,
        min_year: int = 1900,
        max_year: int = 2030
    ) -> 'DataCleaner':
        """
        Filter out records with invalid dates.
        
        Args:
            date_column: Name of date column
            min_year: Minimum valid year
            max_year: Maximum valid year
            
        Returns:
            Self for method chaining
        """
        before = self.df.count()
        
        self.df = self.df.filter(
            (F.year(F.col(date_column)) >= min_year) &
            (F.year(F.col(date_column)) <= max_year)
        )
        
        after = self.df.count()
        removed = before - after
        
        print(f"🔧 Filtered invalid dates: {removed:,} rows removed")
        
        return self
    
    def standardize_column_names(self) -> 'DataCleaner':
        """
        Convert column names to lowercase with underscores.
        
        Returns:
            Self for method chaining
        """
        for col in self.df.columns:
            new_col = col.lower().replace(" ", "_")
            if col != new_col:
                self.df = self.df.withColumnRenamed(col, new_col)
        
        print(f"🔧 Standardized {len(self.df.columns)} column names")
        
        return self
    
    def get_result(self) -> DataFrame:
        """
        Get cleaned DataFrame.
        
        Returns:
            Cleaned Spark DataFrame
        """
        final_count = self.df.count()
        retention_rate = final_count / self.original_count * 100
        
        print(f"\n✅ Cleaning complete:")
        print(f"   Original: {self.original_count:,} rows")
        print(f"   Final: {final_count:,} rows")
        print(f"   Retention: {retention_rate:.1f}%")
        
        return self.df


def clean_patient_data(patients_df: DataFrame) -> DataFrame:
    """
    Clean patient demographics data.
    
    Args:
        patients_df: Raw patients DataFrame
        
    Returns:
        Cleaned patients DataFrame
    """
    cleaner = DataCleaner(patients_df)
    
    return (cleaner
        .remove_duplicates(subset=["person_id"])
        .handle_missing_values(strategy="drop", subset=["person_id", "birth_datetime"])
        .filter_invalid_dates("birth_datetime", min_year=1900, max_year=2024)
        .standardize_column_names()
        .get_result())


def clean_encounter_data(encounters_df: DataFrame) -> DataFrame:
    """
    Clean hospital encounters data.
    
    Args:
        encounters_df: Raw encounters DataFrame
        
    Returns:
        Cleaned encounters DataFrame
    """
    cleaner = DataCleaner(encounters_df)
    
    cleaned = (cleaner
        .remove_duplicates(subset=["visit_occurrence_id"])
        .handle_missing_values(strategy="drop", subset=["visit_occurrence_id", "person_id"])
        .filter_invalid_dates("visit_start_date", min_year=2000, max_year=2024)
        .standardize_column_names()
        .get_result())
    
    # Additional validation: end_date >= start_date
    cleaned = cleaned.filter(
        F.col("visit_end_date") >= F.col("visit_start_date")
    )
    
    return cleaned


# Example usage
if __name__ == "__main__":
    from ..utils.spark_session import get_spark_session
    from ..data_ingestion.bigquery_loader import BigQueryLoader
    
    spark = get_spark_session()
    loader = BigQueryLoader(spark)
    
    # Load and clean patients
    print("\n" + "="*60)
    patients_df = loader.load_patients(limit=1000)
    cleaned_patients = clean_patient_data(patients_df)
    cleaned_patients.show(5)
    
    spark.stop()
