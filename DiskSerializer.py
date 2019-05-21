import asyncio
import pickle

from aiocache.serializers import BaseSerializer


class DiskSerializer(BaseSerializer):
    encoding = None
    def dumps(self, value):
        print('dump')
        print("I've received:\n{}".format(value))
        pickle.dump(value.items(), open('pok_cache/'+str(value.ID)+".pok", 'wb'))
        return value

    def loads(self, value):
        print('load')
        print("I've retrieved:\n{}".format(value))
        #value = pickle.load(open('gamestate.pickle', 'rb'))
        return value
