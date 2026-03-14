"""
Custom Airflow Operator for Great Expectations Validation
Runs data quality checks and sends alerts on failure
"""

from typing import Optional, Dict, Any
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from great_expectations.data_context import DataContext
from great_expectations.core.batch import BatchRequest
import logging

logger = logging.getLogger(__name__)


class GreatExpectationsOperator(BaseOperator):
    """
    Operator to run Great Expectations validation checkpoints
    
    :param checkpoint_name: Name of the Great Expectations checkpoint to run
    :param data_context_root_dir: Path to Great Expectations project directory
    :param fail_task_on_validation_failure: Whether to fail the Airflow task if validation fails
    """
    
    template_fields = ['checkpoint_name', 'batch_kwargs']
    ui_color = '#00A896'
    
    @apply_defaults
    def __init__(
        self,
        checkpoint_name: str,
        data_context_root_dir: str = '/opt/airflow/great_expectations',
        fail_task_on_validation_failure: bool = True,
        batch_kwargs: Optional[Dict[str, Any]] = None,
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.checkpoint_name = checkpoint_name
        self.data_context_root_dir = data_context_root_dir
        self.fail_task_on_validation_failure = fail_task_on_validation_failure
        self.batch_kwargs = batch_kwargs or {}
    
    def execute(self, context):
        """Execute Great Expectations checkpoint"""
        
        logger.info(f"Running Great Expectations checkpoint: {self.checkpoint_name}")
        
        # Load Data Context
        data_context = DataContext(context_root_dir=self.data_context_root_dir)
        
        # Run checkpoint
        result = data_context.run_checkpoint(
            checkpoint_name=self.checkpoint_name,
            batch_request=self.batch_kwargs
        )
        
        # Log results
        success = result["success"]
        statistics = result.get("run_results", {})
        
        logger.info(f"Validation success: {success}")
        logger.info(f"Statistics: {statistics}")
        
        # Push results to XCom for downstream tasks
        context['task_instance'].xcom_push(
            key='validation_results',
            value={
                'success': success,
                'checkpoint_name': self.checkpoint_name,
                'statistics': statistics
            }
        )
        
        if not success and self.fail_task_on_validation_failure:
            raise ValueError(
                f"Great Expectations validation failed for checkpoint: {self.checkpoint_name}"
            )
        
        return result
