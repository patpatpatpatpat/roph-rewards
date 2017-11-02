from datetime import datetime
from random import choice

import robobrowser

from credentials import CREDS_LIST


class ROPH(robobrowser.RoboBrowser):
    INVALID_LOGIN_CODE = 'please try again'

    def __init__(self, username, password, login_url, *args, **kwargs):
        super().__init__(parser='html.parser', **kwargs)

        self.open(login_url)
        login_form = self.get_form()

        if not login_form:
            raise Exception('No form. Probably an ongoing maintenance.')

        login_form['exe_id'] = username
        login_form['password'] = password

        self.submit_form(login_form)

        if self.INVALID_LOGIN_CODE in self.response.text:
            raise Exception('Invalid credentials.')


def claim_daily_login_rewards(cred):
    daily_login_events = [
        {'url': 'https://activities.ragnarokonline.com.ph/daily-login',
         'name': 'Daily Login Oct 2017',
         'end_date': datetime(2017, 11, 14, 23, 59)},
    ]

    for login_event in daily_login_events:
        print('Getting rewards from: %s' % login_event['name'])

        if datetime.today() <= login_event['end_date']:
            roph = ROPH(cred['USERNAME'], cred['PASSWORD'], login_event['url'])
        else:
            print('Sorry, the event already expired.')
            continue

        all_page_links = roph.get_links()

        for link in all_page_links:
            href = link.attrs.get('href', '')
            if 'redeem' in href:
                roph.open(href)  # Simulate clicking of the free item
                # Remove query string from URL
                redeem_link = href.replace('redeem', 'send-items')[:111]
                # Simulate clicking of the OK button to accept the free item
                roph.open(redeem_link)
                print('Reward claimed!')

            if 'share' in href:
                # End of the week reached, simulate sharing page to FB
                # just use redeem-bonus get arg to skip sharing to fb
                redeem_link = href.replace('share', 'redeem-bonus')
                roph.open(redeem_link)
                print('Bonus reward claimed!')


def play_lets_go_hidden(cred):
    """
    News link: https://www.ragnarokonline.com.ph/news/lets-go-hidden
    Event link: https://www.ragnarokonline.com.ph/news/lets-go-hidden

    Start date: Oct. 11, 2017, 4.00 PM
    End date: Nov. 8, 2017, 9.59 AM
    """
    print('Getting rewards from: Let\'s Go Hidden')
    end_date = datetime(2017, 11, 8, 9, 59)

    if not datetime.today() <= end_date:
        print('Sorry, the event already expired.')
        return

    login_url = 'https://activities.ragnarokonline.com.ph/roph-lets-go-hidden/login'
    start_game_url = 'https://activities.ragnarokonline.com.ph/roph-lets-go-hidden/path'
    game_already_joined_today = 'play again tomorrow'
    dead_text = 'You can restart the game after'
    got_item_text = 'You got the item'
    game_conquered = False

    while not game_conquered:
        roph = ROPH(cred['USERNAME'], cred['PASSWORD'], login_url)
        roph.open(start_game_url)
        game_over = False

        paths_taken = 0

        print('Starting new game...')
        while not game_over:
            all_paths = [
                link.attrs.get('href', '') for link in roph.get_links()
                if 'way' in link.attrs.get('href', '')
            ]

            if not all_paths and game_already_joined_today in roph.response.text:
                print('You already played the event today!')
                game_over = True
                game_conquered = True
                continue
            elif not all_paths:
                print('Game over!')
                game_over = True
                continue

            chosen_path = choice(all_paths)
            paths_taken += 1
            print('Selecting path %s' % paths_taken)
            roph.open(chosen_path)

            if dead_text in roph.response.text:
                print('Killed by Bapho!')
            elif got_item_text in roph.response.text:
                print('Item acquired!')
                game_over = True
                game_conquered = True


def main():
    for cred in CREDS_LIST:
        print('Getting rewards for user: %s' % cred['USERNAME'])
        claim_daily_login_rewards(cred)
        play_lets_go_hidden(cred)


if __name__ == "__main__":
    main()
