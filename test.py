from urllib3 import request
import json

my_key:str = '2ac26f2399f9a37167df8c2f58bf7a2d'

def main() -> None:
    #print((json.loads(request('get', 'https://api.themoviedb.org/3/tv/60625/aggregate_credits?api_key=2ac26f2399f9a37167df8c2f58bf7a2d').data))['cast'][0])

    #print(len(json.loads(request('get', 'https://api.themoviedb.org/3/tv/60625/aggregate_credits?api_key=2ac26f2399f9a37167df8c2f58bf7a2d').data)['cast']))

    voice_actor_dict:dict[str, list[str]] = {}
    for voice_actor in json.loads(request('get', 'https://api.themoviedb.org/3/tv/60625/aggregate_credits?api_key=%s'%(my_key)).data)['cast']:
        chars:list[str] = []
        
        for r in voice_actor['roles']:
            for name in r['character'].split(' / '):
                if name.endswith('(voice)'):
                    name = name.split('(')[0][:-1]
                if name == '' or name =='Additional Voices':
                    continue
                chars.append(name)

        if not chars:
            continue

        voice_actor_dict[voice_actor['name']] = chars

    """ print(*voice_actor_dict.items(), sep='\n')
    print(sum([len(v) for v in voice_actor_dict.values()])) """

    #https://rickandmortyapi.com/api/character
    characters_count:int = int(json.loads(request('get', 'https://rickandmortyapi.com/api/character').data)['info']['count'])
    for c in json.loads(request('get', 'https://rickandmortyapi.com/api/character/%s'%(','.join([str(i) for i in range(1, characters_count+1)]))).data)[234:235]:
        print(c)
    

main()

