document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants">
            <strong>Participants:</strong>
            <ul>
              ${
                details.participants.length > 0
                  ? details.participants.map(participant => `<li>${participant}</li>`).join("")
                  : "<li>No participants yet</li>"
              }
            </ul>
          </div>
        `;

        // Add delete icon next to each participant
        const participantsList = activityCard.querySelector(".participants ul");
        participantsList.innerHTML = details.participants.map(participant => `
          <li style="list-style-type: none;">
            ${participant}
            <button class="delete-participant" data-activity="${name}" data-participant="${participant}">❌</button>
          </li>
        `).join("");

        // Add event listener for delete buttons
        participantsList.querySelectorAll(".delete-participant").forEach(button => {
          button.addEventListener("click", async (event) => {
            const activityName = event.target.dataset.activity;
            const participantEmail = event.target.dataset.participant;

            try {
              const response = await fetch(`/activities/${activityName}/unregister?email=${participantEmail}`, {
                method: "POST"
              });

              if (response.ok) {
                // Refresh the activity list dynamically
                fetchActivities();
              } else {
                console.error("Failed to unregister participant.");
              }
            } catch (error) {
              console.error("Error unregistering participant:", error);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh the activity list dynamically
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
