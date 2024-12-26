import time
import psutil
import asyncio
from contextlib import suppress
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator.metrics import (
    requests,
    latency,
)
from src.security import get_db_pool


# Uptime Gauge
uptime_gauge = Gauge("uptime_seconds", "Time since server started in seconds")
start_time = time.time()

# Function to track uptime
def track_uptime():
    uptime_gauge.set(time.time() - start_time)

# System metrics
cpu_usage_gauge = Gauge("cpu_usage_percentage", "CPU usage percentage")
memory_usage_gauge = Gauge("memory_usage_percentage", "Memory usage percentage")

# Function to update cpu usage and memory usage metrics
def update_system_metrics():
    cpu_usage_gauge.set(psutil.cpu_percent())
    memory_usage_gauge.set(psutil.virtual_memory().percent)

# Event to monitor the background collection of metrics
shutdown_event = asyncio.Event()

# Function to collect metrics in the background
async def run_periodic_tasks():
    try:
        while not shutdown_event.is_set():
            # Update system metrics
            update_system_metrics()
            track_uptime()

            # Update user-related metrics
            await update_metrics()
            await asyncio.sleep(10)
    except asyncio.CancelledError:
        # Task was cancelled during shutdown
        print("Periodic metrics task cancelled.")
    finally:
        print("Shutting down periodic metrics collection.")


# User-related metrics
total_users = Gauge("total_users", "Total number of users")
active_users = Gauge("active_users", "Number of active users today")
dau = Gauge("daily_active_users", "Number of active users per day")
wau = Gauge("weekly_active_users", "Number of active users per week")
mau = Gauge("monthly_active_users", "Number of active users per month")

# Helper function to get active users from PostgreSQL
async def get_active_users(period: str):
    query = f"""
        SELECT COUNT(DISTINCT id)
        FROM users
        WHERE last_active >= CURRENT_DATE - INTERVAL '{period}' AND role = 'user';
    """
    db_pool = await get_db_pool()
    async with db_pool.acquire() as conn:  
        result = await conn.fetchval(query)
        await conn.close()
        return result or 0

# Helper function to get the total users
async def get_total_users():
    query = f"""
        SELECT COUNT(id) FROM users
        WHERE role = 'user';
    """
    db_pool = await get_db_pool()
    async with db_pool.acquire() as conn:  
        result = await conn.fetchval(query)
        await conn.close()
        return result or 0

# Function to update all metrics
async def update_metrics():
    # Get the count of active users for different periods
    active_users_today = await get_active_users('1 day')
    active_users_week = await get_active_users('7 days')
    active_users_month = await get_active_users('30 days')
    
    # Update Prometheus metrics
    active_users.set(active_users_today)
    dau.set(active_users_today)
    wau.set(active_users_week)
    mau.set(active_users_month)

    # Update the total users count 
    total_users.set(await get_total_users())

# Function to configure Prometheus instrumentator
def configure_instrumentator():
    instrumentator = Instrumentator(
        should_instrument_requests_inprogress=True
    ).add(
        requests(),
        latency(),
    )
    instrumentator.add(lambda _: uptime_gauge)  # Adding custom metrics
    return instrumentator
