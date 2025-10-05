Feature: User reviews automation status
  As a standard user
  I want to inspect automation activity
  So that I understand which services are running

  Scenario: User cannot change automation states
    Given the operations control center is open
    When I remain in the default user role
    And I attempt to toggle the "Support" automation
    Then I should see "Support automation status: Paused"
    And I should see "Bot controls are locked while in user mode."
