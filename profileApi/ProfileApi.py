import profileApi.dumpor as dumpor
import profileApi.picuki as picuki
import asyncio


def GetProfileData(username=None, userId=None, cursor=None, token=None):
    data = {}
    try:
        data = picuki.getDataFromPicuki(username, userId, cursor, token)
    except Exception as e:
        print(e)
        print('picuki failed')
        try:
            data = asyncio.run(dumpor. GetData(
                username, userId, cursor, token))
        except Exception as e:
            print(e)
            data = {"msg": "error no data"}
    return data
