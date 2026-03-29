"""
Load Testing Script
Simulates 10K-100K concurrent users for performance validation
"""

import asyncio
import aiohttp
import time
import logging
from typing import List
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoadTester:
    """Performance load testing for telehealth platform"""
    
    def __init__(self, base_url: str, num_users: int):
        self.base_url = base_url
        self.num_users = num_users
        self.results = {
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0,
            'response_times': []
        }
    
    async def simulate_user_session(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a user browsing and making a purchase"""
        
        actions = [
            f'/api/products',  # Browse products
            f'/api/products/MEN-ED-001',  # View product details
            f'/api/consultations/start',  # Start consultation
            f'/api/prescriptions',  # Get prescriptions
            f'/api/orders'  # View orders
        ]
        
        for action in actions:
            start_time = time.time()
            
            try:
                async with session.get(f"{self.base_url}{action}") as response:
                    elapsed = (time.time() - start_time) * 1000  # ms
                    
                    if response.status == 200:
                        self.results['successful_requests'] += 1
                    else:
                        self.results['failed_requests'] += 1
                    
                    self.results['response_times'].append(elapsed)
                    
            except Exception as e:
                logger.error(f"Request failed for user {user_id}: {str(e)}")
                self.results['failed_requests'] += 1
            
            # Random delay between actions (0.5-2 seconds)
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def run_load_test(self):
        """Execute load test with concurrent users"""
        logger.info(f"Starting load test with {self.num_users} concurrent users...")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.simulate_user_session(session, user_id)
                for user_id in range(self.num_users)
            ]
            await asyncio.gather(*tasks)
        
        self.results['total_time'] = time.time() - start_time
        self.print_results()
    
    def print_results(self):
        """Print load test results"""
        logger.info("\n" + "="*50)
        logger.info("LOAD TEST RESULTS")
        logger.info("="*50)
        
        total_requests = self.results['successful_requests'] + self.results['failed_requests']
        success_rate = (self.results['successful_requests'] / total_requests * 100) if total_requests > 0 else 0
        
        response_times = self.results['response_times']
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
        p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)] if response_times else 0
        
        logger.info(f"Concurrent Users: {self.num_users}")
        logger.info(f"Total Requests: {total_requests}")
        logger.info(f"Successful: {self.results['successful_requests']}")
        logger.info(f"Failed: {self.results['failed_requests']}")
        logger.info(f"Success Rate: {success_rate:.2f}%")
        logger.info(f"Total Time: {self.results['total_time']:.2f}s")
        logger.info(f"Avg Response Time: {avg_response_time:.2f}ms")
        logger.info(f"P95 Response Time: {p95_response_time:.2f}ms")
        logger.info(f"P99 Response Time: {p99_response_time:.2f}ms")
        
        # Performance assertions
        if avg_response_time < 100:
            logger.info("✅ Average response time < 100ms (PASSED)")
        else:
            logger.warning(f"⚠️  Average response time {avg_response_time:.2f}ms > 100ms")


async def main():
    # Test with increasing load
    test_scenarios = [
        ('Small Load', 100),
        ('Medium Load', 1000),
        ('Large Load', 10000)
    ]
    
    base_url = 'http://localhost:3000'  # Adjust as needed
    
    for scenario_name, num_users in test_scenarios:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {scenario_name}")
        logger.info(f"{'='*50}\n")
        
        tester = LoadTester(base_url, num_users)
        await tester.run_load_test()
        
        # Pause between scenarios
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
