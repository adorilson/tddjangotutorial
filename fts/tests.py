from collections import namedtuple

from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PollInfo = namedtuple('PollInfo', ['question', 'choices'])
POLL1 = PollInfo(
    question = "How awesome is Test-Driven Development?",
    choices = [
        'Very awesome',
        'Quite awesome',
        'Moderately awesome',
    ],
)
POLL2 = PollInfo(
    question = 'Which workshop treat do you prefer?',
    choices = [
        'Beer',
        'Pizza',
        'The Acquisition of Knowledge',
    ],
)

class PollsTest(LiveServerTestCase):
    fixtures = ['admin_user.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_create_new_poll_via_admin_site(self):
        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get(self.live_server_url + '/admin/')

        # She sees the familiar 'Django administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)

        # She types in her username and passwords and hits return
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('adm1n')
        password_field.send_keys(Keys.RETURN)

        # her username and password are accepted, and she is taken to
        # the Site Administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

        # She now sees a couple of hyperlink that says "Polls"
        polls_links = self.browser.find_elements_by_link_text('Polls')
        self.assertEquals(len(polls_links), 2)

        # The second one looks more exciting, so she clicks it
        polls_links[1].click()
        #self.browser.get(self.live_server_url +  '/admin/polls/poll/')

        # She is taken to the polls listing page, which shows she has
        # no polls yet
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('0 polls', body.text)

        # She sees a link to 'add' a new poll, so she clicks it
        new_poll_link = self.browser.find_element_by_link_text('Add poll')
        new_poll_link.click()
        #self.browser.get(self.live_server_url +  '/admin/polls/poll/add/')

        # She sees some input fields for "Question" and "Data published"
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Question:', body.text)
        self.assertIn('Date published:', body.text)

        # She types in an interesting question for the Poll
        question_field = self.browser.find_element_by_name('question')
        question_field.send_keys(u'How awesome is Test-Driven Development?')

        # She sets the date and time of publication - it'll be a new year's poll
        date_field = self.browser.find_element_by_name('pub_date_0')
        date_field.send_keys('01/01/12')
        time_field = self.browser.find_element_by_name('pub_date_1')
        time_field.send_keys('00:00')


        # She sees she can enter choices fot the Poll. She adds three
        choice_1 = self.browser.find_element_by_name('choice_set-0-choice')
        choice_1.send_keys('Very awesome')
        choice_2 = self.browser.find_element_by_name('choice_set-1-choice')
        choice_2.send_keys('Quite awesome')
        choice_3 = self.browser.find_element_by_name('choice_set-2-choice')
        choice_3.send_keys('Moderately awesome')

        # Gertrude clicks the save button
        save_button = self.browser.find_element_by_css_selector("input[value='Save']")
        save_button.click()

        # She is returned to the "Polls" listing, where she can see her
        # new poll, listed as a clickable link
        new_poll_links = self.browser.find_elements_by_link_text(
                       "How awesome is Test-Driven Development?"
                       )
        self.assertEquals(len(new_poll_links), 1)

        # Satisfied, she goes back to sleep

    def _setup_polls_via_admin(self):

        # Gertrude logs into the admin site
        self.browser.get(self.live_server_url + '/admin/')
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('adm1n')
        password_field.send_keys(Keys.RETURN)

        # She has a number of polls to enter . For each one, she:
        for poll_info in [POLL1, POLL2]:
            #Follows the link to Polls app, and adds a new Poll
            self.browser.find_elements_by_link_text('Polls')[1].click()
            self.browser.find_element_by_link_text('Add poll').click()

            # Enter its name, and uses the 'today' and 'now' buttons to set
            # the publish date
            question_field = self.browser.find_element_by_name('question')
            question_field.send_keys(poll_info.question)
            self.browser.find_element_by_link_text('Today').click()
            self.browser.find_element_by_link_text('Now').click()

            # Sees she can entre choices for the Poll on this same page,
            # so she does
            for i, choice_text in enumerate(poll_info.choices):
                choice_field = self.browser.find_element_by_name('choice_set-%d-choice' % i)
                choice_field.send_keys(choice_text)

            # Saves her new poll
            save_button = self.browser.find_element_by_css_selector("input[value='Save']")
            save_button.click()

            # Is returned to the "Polls" listing, where she can her
            # new poll, listed as a clickable link by its name
            new_poll_links = self.browser.find_elements_by_link_text(
                poll_info.question
            )
            self.assertEquals(len(new_poll_links), 1)

            self.browser.get(self.live_server_url + '/admin/')

        # She logs out of the admin site
        self.browser.find_element_by_link_text('Log out').click()

    def test_voting_on_a_new_poll(self):
        # First, Gertrude the administrator logs into admin site and
        # creates a couple of news Polls, and theis response choice_1
        self._setup_polls_via_admin()

        # Now, Herbert the regular user goes to homepage of the site. He
        # sees a list of polls.
        self.browser.get(self.live_server_url)
        heading = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(heading.text, 'Polls')

        # He clicks on the link to the first poll, which is called
        # 'How awesome is Test-Driven Development?'
        first_poll_title = POLL1.question
        self.browser.find_element_by_link_text(first_poll_title).click()

        # He is taken to a poll 'results' page, which says
        # "no-one has voted on this poll yet"
        main_heading = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(main_heading.text, 'Poll Results')
        sub_heading = self.browser.find_element_by_tag_name('h2')
        self.assertEquals(sub_heading.text, first_poll_title)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('No-one has voted on this poll yet', body.text)

        # He also sees a form, which offers him several choices.
        # There are three options with radio buttons
        choice_inputs = self.browser.find_elements_by_css_selector(
                "input[type='radio']"
        )
        self.assertEquals(len(choice_inputs), 3)

        # The buttons have labels to explain them
        choice_labels = self.browser.find_elements_by_tag_name('label')
        choices_text = [c.text for c in choice_labels]
        # TODO to send this patch
        self.assertEquals(choices_text, ['Vote:'] + POLL1.choices)

        # He decided to select "very awesome"
        chosen = self.browser.find_element_by_css_selector(
                "input[value='1']"
        )
        chosen.click()

        # He clicks 'submit'
        self.browser.find_element_by_css_selector(
                "input[type='submit']"
        ).click()

        # The page refreshes, and he sees that his choice
        # has updated the results. They now say
        # "100% : very awesome".
        self.fail('TODO')

        # The page also says "1 votes"

        # Satisfied, he goes back to sleep

