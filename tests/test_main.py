
from moontrader.main import MoonTraderAppTest

def test_moontrader(tmp):
    with MoonTraderAppTest() as app:
        res = app.run()
        print(res)
        raise Exception

def test_command1(tmp):
    argv = ['command1']
    with MoonTraderAppTest(argv=argv) as app:
        app.run()
