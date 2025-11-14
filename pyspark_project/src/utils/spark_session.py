"""
Spark Session Utility - Create and configure PySpark sessions
"""

from pyspark.sql import SparkSession
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


def get_spark_session(
    app_name: str = "HealthcareAnalytics",
    config_path: Optional[str] = None,
    local: bool = True
) -> SparkSession:
    """
    Create or get existing Spark session with healthcare-optimized configs.
    
    Args:
        app_name: Name of the Spark application
        config_path: Path to spark_config.yaml file
        local: If True, run locally. If False, run on cluster.
        
    Returns:
        SparkSession configured for healthcare data processing
        
    Example:
        >>> spark = get_spark_session(local=True)
        >>> df = spark.read.parquet("data/raw/patients.parquet")
    """
    
    builder = SparkSession.builder.appName(app_name)
    
    # Load configuration from YAML if provided
    if config_path:
        config = _load_spark_config(config_path)
        for key, value in config.get("spark", {}).items():
            builder = builder.config(key, value)
    else:
        # Default configurations
        if local:
            builder = builder.master("local[*]")
        
        # Memory settings
        builder = builder.config("spark.executor.memory", "4g")
        builder = builder.config("spark.driver.memory", "4g")
        
        # SQL optimizations
        builder = builder.config("spark.sql.adaptive.enabled", "true")
        builder = builder.config("spark.sql.shuffle.partitions", "200")
        
        # Serialization
        builder = builder.config(
            "spark.serializer", 
            "org.apache.spark.serializer.KryoSerializer"
        )
        
        # BigQuery connector (for GCP integration)
        builder = builder.config(
            "spark.jars.packages",
            "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.32.2"
        )
    
    # Create session
    spark = builder.getOrCreate()
    
    # Set log level
    spark.sparkContext.setLogLevel("WARN")
    
    print(f"✅ Spark session created: {app_name}")
    print(f"   Version: {spark.version}")
    print(f"   Master: {spark.sparkContext.master}")
    
    return spark


def _load_spark_config(config_path: str) -> Dict[str, Any]:
    """Load Spark configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def stop_spark_session(spark: SparkSession) -> None:
    """
    Stop the Spark session and clean up resources.
    
    Args:
        spark: SparkSession to stop
    """
    spark.stop()
    print("🛑 Spark session stopped")


# Example usage
if __name__ == "__main__":
    # Create local Spark session
    spark = get_spark_session(local=True)
    
    # Show Spark UI URL
    print(f"\n📊 Spark UI: {spark.sparkContext.uiWebUrl}")
    
    # Test with sample data
    data = [
        ("patient_001", "John Doe", 45, "Diabetes"),
        ("patient_002", "Jane Smith", 62, "Hypertension"),
        ("patient_003", "Bob Johnson", 38, "Asthma"),
    ]
    
    df = spark.createDataFrame(
        data, 
        ["patient_id", "name", "age", "condition"]
    )
    
    print("\n📋 Sample DataFrame:")
    df.show()
    
    # Clean up
    stop_spark_session(spark)
