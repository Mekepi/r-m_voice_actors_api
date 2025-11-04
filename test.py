from urllib3 import request
import json

my_key:str = '2ac26f2399f9a37167df8c2f58bf7a2d'

def main() -> None:
    voice_actors:list[dict] = json.loads(request('get', 'https://api.themoviedb.org/3/tv/60625/aggregate_credits?api_key=%s'%(my_key)).data)['cast']
    
    char_to_va:dict[str, tuple[str, str]] = {}
    for voice_actor in voice_actors:
        
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

        char_to_va.update([(c, (voice_actor['name'], 'https://www.themoviedb.org/person/%s'%(voice_actor['id']))) for c in chars])
    
    characters_count:int = int(json.loads(request('get', 'https://rickandmortyapi.com/api/character').data)['info']['count'])
    characters_list:list[dict[str, dict]] = json.loads(request('get', 'https://rickandmortyapi.com/api/character/%s'%(','.join([str(i) for i in range(1, characters_count+1)]))).data)


    c_names:list[str] = [c['name'] for c in characters_list]
    #print(c_names[0])

    va_to_char:dict[str, tuple[str, list[str]]] = {}
    for c, va in char_to_va.items():
        if c not in c_names:
            continue
        if va[0] not in va_to_char:
            va_to_char[va[0]] = (va[1], [])
        
        va_to_char[va[0]][1].append(c)

    #va_to_char sample: 'Ice-T': ('https://www.themoviedb.org/person/21411', ['Magma-Q'])

    episodes_count:int = int(json.loads(request('get', 'https://rickandmortyapi.com/api/character').data)['info']['count'])
    episodes_dict:dict[str, dict] = json.loads(request('get', 'https://rickandmortyapi.com/api/episodes/%s'%(','.join([str(i) for i in range(1, characters_count+1)]))).data)

    """ episode sample: 
    {
    "id": 10,
    "name": "Close Rick-counters of the Rick Kind",
    "air_date": "April 7, 2014",
    "episode": "S01E10",
    "characters": [
      "https://rickandmortyapi.com/api/character/1",
      "https://rickandmortyapi.com/api/character/2",
      // ...
    ],
    "url": "https://rickandmortyapi.com/api/episode/10",
    "created": "2017-11-10T12:56:34.747Z"
  } """

main()

