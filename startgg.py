from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import main


async def set_entrants(target):
    print("set_entrants called")
    transport = AIOHTTPTransport(url='https://api.start.gg/gql/alpha',
                                 headers={"Authorization": "Bearer 78daf09295ea46605a37caf953448871"})

    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(
        """
    query($setID: ID!){
    set(id: $setID){
        slots{
        standing{
            entrant{
            id
            }
        }
        }   
    }
    }       
    """
    )
    target = str(target)
    target = target[7:-1]
    print(target)
    params = {"setID": target}
    result = await client.execute_async(query, variable_values=params)
    print("result "+ str(result))
    p1 = result['set']['slots'][0]['standing']['entrant']['id']
    p2 = result['set']['slots'][1]['standing']['entrant']['id']
    temp_list = [target, p1, p2]
    print("temp_list "+str(temp_list))
    return temp_list


async def chain_locate_started(event_id):
    cursor = main.cursor
    sets = await locate_started(event_id)
    results = []
    cursor.execute("SELECT startID FROM processed_sets_started")
    processed_sets = []
    for j in cursor:
        j = str(j)
        j = j[2:-3]
        processed_sets.append(j)
    for i in range(len(sets)):
        id = str(sets[i])
        id = id[7:-1]
        if id in processed_sets:
            print("skipped set")
        else:
            out = await set_entrants(sets[i])
            results.append(out)
    return results


async def locate_started(event_id):
    transport = AIOHTTPTransport(url='https://api.start.gg/gql/alpha',
                                 headers={"Authorization": "Bearer 78daf09295ea46605a37caf953448871"})
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(
        """
       query($eventID: ID!, $page: Int!, $perPage: Int!){
  event(id: $eventID){
    sets(
      page: $page,
      perPage: $perPage,
      sortType: STANDARD
  	){
  	nodes{
      id
    }
  }
}
}  
        """
    )
    params = {"eventID": event_id, "page": 1, "perPage": 50}
    result = await client.execute_async(query, variable_values=params)
    sets = result['event']['sets']['nodes']
    targets = []
    count = 0
    for _ in sets:
        x = sets[count]
        count +=1
        targets.append(x)
    print(targets)
    return targets


async def get_ids(tourney_id):
    transport = AIOHTTPTransport(url='https://api.start.gg/gql/alpha',
                                 headers={"Authorization": "Bearer 78daf09295ea46605a37caf953448871"})
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(
        """
query($tourneySlug: String!) {
  tournament(slug: $tourneySlug) {
    events{
      id
      entrants{
        nodes{
          name
          id
        }
      }
    }
  }
}

        """
    )
    params = {"tourneySlug": tourney_id}
    ids = await client.execute_async(query,variable_values=params)
    event_id = ids['tournament']['events'][0]['id']
    entrants = ids['tournament']['events'][0]['entrants']['nodes']
    return event_id, entrants
