Makeup Dashboard

This repository contains an interactive dashboard for exploring makeup product data.

1. Clone the Repository
git clone https://github.com/micahcheng/sephora-dashboard.git
cd sephora-dashboard

2. Install the Required Packages
Using Conda (recommended)
conda create -n sephora python=3.10
conda activate sephora
pip install panel hvplot pandas numpy bokeh

Using Pip
pip install panel hvplot pandas numpy bokeh

3. Run the Dashboard (Important)

Do not run:

python makeup_panel.py


This will not launch the dashboard.

Instead, run:

panel serve makeup_panel.py --autoreload --show

4. Open the Dashboard

The dashboard should open automatically.
If not, you can access it at:

http://localhost:5006/makeup_panel
