let selectedView = null;

const atcButton = document.getElementById('atcButton');
const pilotButton = document.getElementById('pilotButton');
const confirmButton = document.getElementById('confirmButton');
const viewSpecificButtons = document.getElementById('viewSpecificButtons');

atcButton.onclick = function() {
  selectedView = 'atc';
  confirmButton.style.display = 'inline-block';  // Show the confirmation button
};

pilotButton.onclick = function() {
  selectedView = 'pilot';
  confirmButton.style.display = 'inline-block';  // Show the confirmation button
};

confirmButton.onclick = function() {
  // Hide the selection menu and show specific view buttons
  confirmButton.style.display = 'none';  // Hide the confirmation button
  showViewSpecificButtons();
};

function showViewSpecificButtons() {
  viewSpecificButtons.style.display = 'flex';

  // Clear any previous buttons
  viewSpecificButtons.innerHTML = '';

  // ATC View Buttons
  if (selectedView === 'atc') {
    viewSpecificButtons.innerHTML += `
      <button class="view-specific-button">Fatigue Alerts</button>
      <button class="view-specific-button">Real-time Flight Information</button>
      <button class="view-specific-button">Runway Allocation</button>
      <button class="view-specific-button">Pop-up Commands</button>
      <button class="view-specific-button">Communication Panel</button>
    `;
  }

  // Pilot View Buttons
  else if (selectedView === 'pilot') {
    viewSpecificButtons.innerHTML += `
      <button class="view-specific-button">Fatigue Monitoring</button>
      <button class="view-specific-button">Runway Information</button>
      <button class="view-specific-button">ATC Commands</button>
      <button class="view-specific-button">Communication Panel</button>
      <button class="view-specific-button">Flight Alerts</button>
    `;
  }
}