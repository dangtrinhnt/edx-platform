"""
Acceptance tests for Studio.
"""
from bok_choy.web_app_test import WebAppTest

from ..pages.studio.asset_index import AssetIndexPage
from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.studio.checklists import ChecklistsPage
from ..pages.studio.course_import import ImportPage
from ..pages.studio.course_info import CourseUpdatesPage
from ..pages.studio.edit_tabs import PagesPage
from ..pages.studio.export import ExportPage
from ..pages.studio.howitworks import HowitworksPage
from ..pages.studio.index import DashboardPage
from ..pages.studio.login import LoginPage
from ..pages.studio.manage_users import CourseTeamPage
from ..pages.studio.overview import CourseOutlinePage
from ..pages.studio.settings import SettingsPage
from ..pages.studio.settings_advanced import AdvancedSettingsPage
from ..pages.studio.settings_graders import GradingPage
from ..pages.studio.signup import SignupPage
from ..pages.studio.textbooks import TextbooksPage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc

from .helpers import UniqueCourseTest


class LoggedOutTest(WebAppTest):
    """
    Smoke test for pages in Studio that are visible when logged out.
    """

    def setUp(self):
        super(LoggedOutTest, self).setUp()
        self.pages = [LoginPage(self.browser), HowitworksPage(self.browser), SignupPage(self.browser)]

    def test_page_existence(self):
        """
        Make sure that all the pages are accessible.
        Rather than fire up the browser just to check each url,
        do them all sequentially in this testcase.
        """
        for page in self.pages:
            page.visit()


class LoggedInPagesTest(WebAppTest):
    """
    Tests that verify the pages in Studio that you can get to when logged
    in and do not have a course yet.
    """

    def setUp(self):
        super(LoggedInPagesTest, self).setUp()
        self.auth_page = AutoAuthPage(self.browser, staff=True)
        self.dashboard_page = DashboardPage(self.browser)

    def test_dashboard_no_courses(self):
        """
        Make sure that you can get to the dashboard page without a course.
        """
        self.auth_page.visit()
        self.dashboard_page.visit()


class CoursePagesTest(UniqueCourseTest):
    """
    Tests that verify the pages in Studio that you can get to when logged
    in and have a course.
    """

    COURSE_ID_SEPARATOR = "."

    def setUp(self):
        """
        Install a course with no content using a fixture.
        """
        super(CoursePagesTest, self).setUp()

        CourseFixture(
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run'],
            self.course_info['display_name']
        ).install()

        self.auth_page = AutoAuthPage(self.browser, staff=True)

        self.pages = [
            clz(self.browser, self.course_info['org'], self.course_info['number'], self.course_info['run'])
            for clz in [
                AssetIndexPage, ChecklistsPage, ImportPage, CourseUpdatesPage,
                PagesPage, ExportPage, CourseTeamPage, CourseOutlinePage, SettingsPage,
                AdvancedSettingsPage, GradingPage, TextbooksPage
            ]
        ]

    def test_page_existence(self):
        """
        Make sure that all these pages are accessible once you have a course.
        Rather than fire up the browser just to check each url,
        do them all sequentially in this testcase.
        """
        # Log in
        self.auth_page.visit()

        # Verify that each page is available
        for page in self.pages:
            page.visit()


class DiscussionPreviewTest(UniqueCourseTest):
    """
    Tests that Inline Discussions are rendered with a custom preview in Studio
    """

    def setUp(self):
        super(DiscussionPreviewTest, self).setUp()
        CourseFixture(**self.course_info).add_children(
            XBlockFixtureDesc("chapter", "Test Section").add_children(
                XBlockFixtureDesc("sequential", "Test Subsection").add_children(
                    XBlockFixtureDesc("vertical", "Test Unit").add_children(
                        XBlockFixtureDesc(
                            "discussion",
                            "Test Discussion",
                        )
                    )
                )
            )
        ).install()

        AutoAuthPage(self.browser, staff=True).visit()
        cop = CourseOutlinePage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )
        cop.visit()
        self.unit = cop.section('Test Section').subsection('Test Subsection').toggle_expand().unit('Test Unit')
        self.unit.go_to()

    def test_is_preview(self):
        """
        Ensure that the preview version of the discussion is rendered.
        """
        self.assertTrue(self.unit.q(css=".discussion-preview").present)
        self.assertFalse(self.unit.q(css=".discussion-show").present)
