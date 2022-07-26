from .models import BananaModel, ModelResults
from .configs import BananaConfig
from .client import BananaClient, BananaRun

# compat layer for old API through aliasing
run = BananaRun.run
start = BananaRun.start
check = BananaRun.check

async_run = BananaRun.async_run
async_start = BananaRun.async_start
async_check = BananaRun.async_check

