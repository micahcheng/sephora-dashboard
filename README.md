# makeup-dashboard
1. Clone the repository
git clone https://github.com/micahcheng/sephora-dashboard.git
cd sephora-dashboard

2. Install the required packages

If using conda:

conda create -n sephora python=3.10
conda activate sephora
pip install panel hvplot pandas numpy bokeh


Or using pip:

pip install panel hvplot pandas numpy bokeh
3. Run the dashboard (IMPORTANT)

❌ Do NOT run:

python makeup_panel.py


(This will NOT open the dashboard.)

✔ INSTEAD run:

panel serve makeup_panel.py --autoreload --show

4. Open dashboard in browser

After running the above command, the dashboard will appear automatically, or you can open:

http://localhost:5006/makeup_panel
