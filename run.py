# get data
from data_parser import getData

# initialize dash app
from DashApp.app import app
import DashApp.index

if __name__ == "__main__":
    getData() # cache data so the graphs are responsive
    app.run_server(debug=True, use_reloader=False, dev_tools_hot_reload=False)