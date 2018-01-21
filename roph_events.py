import sys
from datetime import datetime
from random import choice

import robobrowser
from werkzeug.exceptions import BadRequestKeyError

from credentials import CREDS_LIST


class ROPH(robobrowser.RoboBrowser):
    INVALID_LOGIN_CODE = 'please try again'

    def __init__(self, username, password, login_url, *args, **kwargs):
        super().__init__(parser='html.parser', **kwargs)

        self.open(login_url)
        login_form = self.get_form()

        if not login_form:
            raise Exception('No form. Probably an ongoing maintenance.')

        try:
            login_form['exe_id'] = username
        except BadRequestKeyError:
            try:
                login_form['exeid'] = username
            except BadRequestKeyError:
                login_form['username'] = username
        login_form['password'] = password

        self.submit_form(login_form)

        if self.INVALID_LOGIN_CODE in self.response.text:
            raise Exception('Invalid credentials.')


def claim_daily_login_rewards(cred):
    daily_login_events = [
        {'url': 'https://activities.ragnarokonline.com.ph/daily-login',
         'name': 'Daily Login Jan 2018',
         'end_date': datetime(2018, 2, 14, 23, 59)},
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

                item_name = None
                latest_items = roph.select('.BoxItem.disabled')

                if latest_items:
                    last_item_received = latest_items[-1]
                    day, item_name = filter(None, last_item_received.text.splitlines())
                    print('Reward claimed @ Day {day}: {item_name}'.format(day=day, item_name=item_name))

            if 'share' in href:
                # End of the week reached, simulate sharing page to FB
                roph.open(href)
                # Then use redeem-bonus get arg to skip sharing to FB
                redeem_link = href.replace('share', 'redeem-bonus')
                roph.open(redeem_link)

                bonus_item = roph.select('#items_name')

                if bonus_item:
                    print('Bonus reward claimed: %s' % bonus_item[0].text)


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
    acquired_item_class = '.text-item.text-center'
    path_option_indicator = 'way'

    while not game_conquered:
        roph = ROPH(cred['USERNAME'], cred['PASSWORD'], login_url)
        roph.open(start_game_url)
        game_over = False

        paths_taken = 0

        print('Starting new game...')
        while not game_over:
            all_paths = [
                link.attrs.get('href', '') for link in roph.get_links()
                if path_option_indicator in link.attrs.get('href', '')
            ]

            if not all_paths and game_already_joined_today in roph.response.text:
                acquired_items = roph.select(acquired_item_class)
                if acquired_items:
                    acquired_item = acquired_items[0].text

                print('Item acquired: %s' % acquired_item)
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
                acquired_items = roph.select(acquired_item_class)
                if acquired_items:
                    acquired_item = acquired_items[0].text

                print('Item acquired: %s' % acquired_item)
                game_over = True
                game_conquered = True


def redeem_items_from_code(credentials, code):
    """
    `credentials`: Dictionary containing the user's username & password
    `code`: Item code for redeeming items. Example: FEWY-DD9V-EZZ1-KA1G
    """
    login_url = 'https://www.ragnarokonline.com.ph/login'
    redeem_url = 'https://www.ragnarokonline.com.ph/itemcode'
    redemption_history_url = 'https://www.ragnarokonline.com.ph/itemcode/history'
    possible_errors = [
        'The itemcode format is invalid.',
        'An item code could not be found in the system.',
        'The used count per account has reached limit.',
    ]
    latest_rewards_list_class = 'tr .col-xs-4'
    item_quantity_indicator = 'x'  # Examples: Miracle Tonic x2, Siege White Potion x150

    browser = ROPH(credentials['USERNAME'], credentials['PASSWORD'], login_url)

    print('Getting rewards via item code: %s' % code)
    browser.open(redeem_url)
    redeem_form = browser.get_form()
    redeem_form['itemcode'] = code
    browser.submit_form(redeem_form)
    code_is_invalid = any([error in browser.response.text for error in possible_errors])

    if code_is_invalid:
        print('Item code invalid or already used.')
        return

    browser.open(redemption_history_url)

    if browser.select(latest_rewards_list_class):
        cleaned_item_list = []
        latest_reward_index = 1  # Index 0 is table header
        items_from_latest_redemption = [
            item.strip() for item in
            browser.select(latest_rewards_list_class)[latest_reward_index].text.splitlines()
        ]
        items_from_latest_redemption = list(filter(None, items_from_latest_redemption))

        for i, item in enumerate(items_from_latest_redemption):
            try:
                next_item_index = i + 1
                if items_from_latest_redemption[next_item_index].startswith(item_quantity_indicator):
                    item_quantity = items_from_latest_redemption[next_item_index]
                    cleaned_item_list.append('- {} {}'.format(item, item_quantity))
                elif not item.startswith(item_quantity_indicator):
                    cleaned_item_list.append('- ' + item)  # Actual item name
            except IndexError:
                pass

        print('You got:')
        print('\n'.join(cleaned_item_list))
        return

    print('Nothing redeemed.')


def play_midgard_adventure(cred):
    print('Getting rewards from: Midgard Adventure')
    end_date = datetime(2018, 2, 14, 9, 59)

    if not datetime.today() <= end_date:
        print('Sorry, the event already expired.')
        return

    MAX_ROLLS_REACHED_ERROR = 'Unprocessable Entity'
    LEVEL_REQUIREMENT_NOT_REACHED_ERROR = 'Level is lower then required.'
    login_url = 'https://acts.ragnarokonline.com.ph/snake-ladders/ragnarok-philippines/ph-snake-ladder-jan-2018/login'
    share_url = 'https://acts.ragnarokonline.com.ph/snake-ladders/ragnarok-philippines/ph-snake-ladder-jan-2018/shared'
    acquired_item_class = '.item-detail'

    browser = ROPH(cred['USERNAME'], cred['PASSWORD'], login_url)

    print('Playing Midgard Adventure...')
    while True:
        roll_dice_form = browser.get_form()
        browser.submit_form(roll_dice_form)

        if MAX_ROLLS_REACHED_ERROR in browser.response.text:
            print('Maximum dice rolls for today reached.')
            break
        if LEVEL_REQUIREMENT_NOT_REACHED_ERROR in browser.response.text:
            print('You cannot play because you do not have a level 50 character.')
            break

        acquired_item = browser.select(acquired_item_class)

        if acquired_item and 'waiting' not in acquired_item[0].text:
            print('You got: %s' % acquired_item[0].text)

        print('Faking FaceBook share to enable dice rolling...')
        browser.open(share_url)


def claim_rewards(code=None):
    for cred in CREDS_LIST:
        print('------------------------------------------------')
        print('User: %s' % cred['USERNAME'])
        claim_daily_login_rewards(cred)
        play_midgard_adventure(cred)

        if code:
            redeem_items_from_code(cred, code)


def play_matching_cards(cred):
    """
    News link: https://www.ragnarokonline.com.ph/news/card-matching
    """
    CARD_OPTION_FORMAT = 'https://activities.ragnarokonline.com.ph/matching-cards/play?card=%s'
    share_url = 'https://activities.ragnarokonline.com.ph/matching-cards/share'
    login_url = 'https://activities.ragnarokonline.com.ph/matching-cards/login'
    cannot_play_game_error = 'Your ID does not contain a 50 level character.'

    def get_emerald_count(br):
        emerald_count_class = '.point-aw'
        return br.select(emerald_count_class)[0].text

    def get_remaining_chances_count(br):
        remaining_chances_class = '.logid-pointday'
        return int(browser.select(remaining_chances_class)[0].text.strip())

    def get_card_number(card_option):
        return card_option.split('=')[-1]

    print('Getting rewards from: Card Matching')
    end_date = datetime(2017, 12, 13, 9, 59)

    if not datetime.today() <= end_date:
        print('Sorry, the event already expired.')
        return

    browser = ROPH(cred['USERNAME'], cred['PASSWORD'], login_url)

    if cannot_play_game_error in browser.response.text:
        print(cannot_play_game_error)
        return

    remaining_chances = get_remaining_chances_count(browser)
    all_card_options = [
        link.attrs.get('href', '') for link in browser.get_links()
        if 'play?card' in link.attrs.get('href', '')
    ]
    cards_and_values = {
        get_card_number(card): None for card in all_card_options
    }

    claimed_bonus_chances = False
    match_card_number = None
    last_picked_card_value = None
    last_picked_card_number = None

    # Start card matching
    print('Number of Emeralds: %s' % get_emerald_count(browser))
    print('Remaining chances: %s' % remaining_chances)

    while True:
        if remaining_chances == 0 and not claimed_bonus_chances:
            browser.open(share_url)
            print('Faked FB share to increase chances by %s' % get_remaining_chances_count(browser))
            remaining_chances = get_remaining_chances_count(browser)
            claimed_bonus_chances = True

        if remaining_chances == 0 and claimed_bonus_chances:
            break

        # Check for matches every after 2 picks
        if remaining_chances % 2 == 0:
            pairs = []
            for card_number in cards_and_values.keys():
                if list(cards_and_values.values()).count(cards_and_values[card_number]) == 2:
                    pairs.append(card_number)

            if pairs:
                browser.open(CARD_OPTION_FORMAT % pairs[0])
                browser.open(CARD_OPTION_FORMAT % pairs[1])
                print('Matched cards #%s & #%s! You gained 1 emerald!' % (pairs[0], pairs[1]))
                remaining_chances -= 2
                cards_and_values.pop(pairs[0])
                cards_and_values.pop(pairs[1])
                last_picked_card_value = None
                last_picked_card_number = None
                match_card_number = None
                continue

        if match_card_number:
            chosen_card = CARD_OPTION_FORMAT % match_card_number
            browser.open(chosen_card)
            print('Matched with #%s! You gained 1 emerald!' % match_card_number)

            try:
                cards_and_values.pop(match_card_number)
                cards_and_values.pop(last_picked_card_number)
            except KeyError:
                pass
            match_card_number = None
            last_picked_card_value = None
            last_picked_card_number = None
            remaining_chances -= 1
            continue

        chosen_card = choice(all_card_options)
        chosen_card_number = get_card_number(chosen_card)
        all_card_options.remove(chosen_card)

        browser.open(chosen_card)
        chosen_card_value = browser.select('#card-%s img' % chosen_card_number)[0].attrs.get('src')

        if remaining_chances % 2 == 1 and last_picked_card_value == chosen_card_value:
            # Inform user if the 2 randomly picked cards matched
            print('Randomly matched with #%s! You gained 1 emerald!' % chosen_card_number)
            cards_and_values.pop(last_picked_card_number)
            last_picked_card_value = None
            last_picked_card_number = None
            remaining_chances -= 1
            continue

        else:
            print('Picking card #%s...' % chosen_card_number)

            if chosen_card_value in cards_and_values.values():
                values_to_cards = {
                    value: key for key, value in cards_and_values.items()
                }
                match_card_number = values_to_cards[chosen_card_value]
                cards_and_values[chosen_card_number] = chosen_card_value
            else:
                cards_and_values[chosen_card_number] = chosen_card_value
                print('No match found.')

        remaining_chances -= 1
        last_picked_card_value = chosen_card_value
        last_picked_card_number = chosen_card_number

    print('No chances remaining. Play again tomorrow.')
    print('Number of Emeralds: %s' % get_emerald_count(browser))


if __name__ == "__main__":
    code = None

    if len(sys.argv) > 1:
        code = sys.argv[1]

    claim_rewards(code)
