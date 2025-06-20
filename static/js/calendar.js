document.addEventListener("DOMContentLoaded", function () {
  const calendarGrid = document.getElementById("calendarGrid");
  const monthYear = document.getElementById("monthYear");
  const prevBtn = document.getElementById("prevMonthBtn");
  const nextBtn = document.getElementById("nextMonthBtn");
  const modal = document.getElementById("eventModal");
  const eventInput = document.getElementById("eventInput");
  const eventDateText = document.getElementById("eventDateText");
  const saveBtn = document.getElementById("saveEventBtn");
  const closeModal = document.querySelector(".modal .close");

  let currentDate = new Date();
  let selectedDate = null;
  let allEvents = [];

  function formatDate(date) {
    return date.toISOString().split("T")[0];
  }

  function fetchEvents() {
    fetch("/events/api/")
      .then(res => res.json())
      .then(data => {
        allEvents = data;
        renderCalendar();
      })
      .catch(err => {
        console.error("Error loading events:", err);
        calendarGrid.innerHTML = `<p style="grid-column: span 7; color: black;">Please login first...</p>`;
      });
  }

  function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDay = firstDay.getDay();
    const totalDays = lastDay.getDate();

    calendarGrid.innerHTML = "";

    // Add weekday labels
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    weekdays.forEach(day => {
      const div = document.createElement("div");
      div.classList.add("weekday-label");
      div.textContent = day;
      calendarGrid.appendChild(div);
    });

    // Blank before 1st
    for (let i = 0; i < startDay; i++) {
      const empty = document.createElement("div");
      empty.classList.add("day", "inactive");
      calendarGrid.appendChild(empty);
    }

    for (let day = 1; day <= totalDays; day++) {
      const date = new Date(year, month, day);
      const dateStr = formatDate(date);

      const dayBox = document.createElement("div");
      dayBox.classList.add("day");

      if (new Date().toDateString() === date.toDateString()) {
        dayBox.classList.add("today");
      }

      const dateNumber = document.createElement("div");
      dateNumber.classList.add("date-number");
      dateNumber.textContent = day;
      dayBox.appendChild(dateNumber);

      const dayEvents = allEvents.filter(e => e.date === dateStr);
      dayEvents.forEach(e => {
        const tag = document.createElement("div");
        tag.classList.add("event-box", e.event_type === "admin" ? "admin-event-box" : "user-event-box");
        tag.textContent = e.title;

        // Add delete button if user-created
        if (e.event_type === "user" && e.id) {
          const delBtn = document.createElement("span");
          delBtn.textContent = "❌";
          delBtn.classList.add("delete-btn");
          delBtn.title = "Delete";
          delBtn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            if (confirm("Delete this event?")) {
              deleteEvent(e.id);
            }
          });
          tag.appendChild(delBtn);
        }

        dayBox.appendChild(tag);
      });

      dayBox.addEventListener("click", () => {
        selectedDate = dateStr;
        eventDateText.textContent = `Add event on ${selectedDate}`;
        eventInput.value = "";
        modal.style.display = "flex";
      });

      calendarGrid.appendChild(dayBox);
    }

    monthYear.textContent = `${firstDay.toLocaleString("default", { month: "long" })} ${year}`;
  }

  function deleteEvent(eventId) {
    fetch(`/events/delete/${eventId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          fetchEvents();
        } else {
          alert("Failed to delete event.");
        }
      })
      .catch(err => {
        console.error("Delete failed:", err);
      });
  }

  saveBtn.addEventListener("click", () => {
    const title = eventInput.value.trim();
    if (!title || !selectedDate) {
      alert("Please enter a valid title.");
      return;
    }

    fetch("/events/save/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ title, date: selectedDate }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          modal.style.display = "none";
          fetchEvents();
        } else {
          alert("Error saving event: " + (data.message || "Unknown error"));
        }
      })
      .catch(err => {
        console.error("Save failed:", err);
        alert("Failed to save event.");
      });
  });

  closeModal.addEventListener("click", () => {
    modal.style.display = "none";
  });

  prevBtn.addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
  });

  nextBtn.addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
  });

  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  fetchEvents();
});
