from ast import Num
import webbrowser


def open_algo_explorer(app_id: int):
    url = f"https://testnet.algoexplorer.io/application/{app_id}"
    webbrowser.open(url)
