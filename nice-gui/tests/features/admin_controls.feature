Feature: Admin manages automation suite
  As an administrator
  I want to coordinate automations and billing
  So that our tenant stays within credit budgets

  Scenario: Activate the announcements automation
    Given the operations control center is open
    When I switch to the admin role
    And I activate the "Announcements" automation
    Then I should see "Announcements automation status: Active"
    And I should see "Credits used: 200 / 320"
    And I should see "Announcements automation activated"

  Scenario: Pause the support automation
    Given the operations control center is open
    When I switch to the admin role
    And I deactivate the "Support" automation
    Then I should see "Support automation status: Paused"
    And I should see "Credits used: 160 / 320"
    And I should see "Support automation paused"
