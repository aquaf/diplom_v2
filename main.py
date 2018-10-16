import requests
import time
import json
import progressbar

api_address = 'https://api.vk.com/method/'
token = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'

params = {
    'access_token': token,
    'v': '5.85'
}


def get_user_id(name):
    """Возвращает id пользователя"""
    if name.isalpha():
        return requests.get(f'{api_address}utils.resolveScreenName?screen_name={name}', params).json()['response'][
            "object_id"]
    else:
        return name


def get_user_friends(id):
    """Возвращает список друзей пользователя"""
    return requests.get(f'{api_address}friends.get?user_id={id}', params)


def get_user_groups(id):
    """Возвращает список групп пользователя"""
    return requests.get(f'{api_address}groups.get?user_id={id}', params)


def spy_game():
    """Возвращает список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей"""
    name = input('Введите login или id пользователя: ')
    user_id = get_user_id(f'{name}')
    user_friends = get_user_friends(user_id).json()['response']['items']
    user_groups = get_user_groups(user_id).json()['response']['items']
    groups_without_friends = []
    with progressbar.ProgressBar(max_value=len(user_groups)) as bar:
        for num, group in enumerate(user_groups):
            try:
                response_group_members = set(
                    (requests.get(f'{api_address}groups.getMembers?group_id={group}&user_id{user_id}&filter=friends',
                                  params)).json()['response'][
                        'items'])
                if response_group_members.isdisjoint(user_friends):
                    groups_without_friends.append(group)
            except:
                pass
            time.sleep(1)
            bar.update(num)
    groups_without_friends = [str(i) for i in groups_without_friends]
    groups_without_friends_json = \
        requests.get(f'{api_address}groups.getById?group_ids={", ".join(groups_without_friends)}&fields=members_count',
                     params).json()[
            'response']
    group_list_final = []
    for i in groups_without_friends_json:
        group_list_final.append({'name': i['name'], 'gid': i['id'], 'members_count': i['members_count']})
    return group_list_final


if __name__ == "__main__":
    with open("groups.json", "w", encoding="utf-8") as file:
        json.dump(spy_game(), file, ensure_ascii=False)
