from typing import List, Optional

from external.github_api.graphql.user import (
    get_user_followers as _get_user_followers,
    get_user_following as _get_user_following,
)
from models.user.followers import User, UserFollowers


def get_user_followers(user_id: str) -> UserFollowers:
    """get user followers and users following for given user"""

    followers: List[User] = []
    following: List[User] = []

    for user_list, get_func in zip(
        [followers, following], [_get_user_followers, _get_user_following]
    ):
        after: Optional[str] = ""
        index, cont = 0, True  # initialize variables
        while cont and index < 10:
            try:
                after_str: str = after if isinstance(after, str) else ""
                data = get_func(user_id, after=after_str)
            except Exception as e:
                raise e

            cont = False

            user_list.extend(
                map(
                    lambda x: User(name=x.name, login=x.login, url=x.url),
                    data.nodes,
                )
            )
            if data.page_info.has_next_page:
                after = data.page_info.end_cursor
                cont = True

            index += 1

    output = UserFollowers(followers=followers, following=following)
    return output
