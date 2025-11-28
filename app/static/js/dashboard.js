document.addEventListener("DOMContentLoaded", function () {

    const tabs = document.querySelectorAll(".tab");
    const contents = document.querySelectorAll(".tab-content");
    const log_period_btn = document.querySelector(".log-period-btn");
    const logoutForm = document.getElementById("logout-form");

    let calendarRendered = false; // render calendar only once
    let calendar; // make calendar variable available

    // make calendar variable available now
    (function initCalendar() {
        if (typeof FullCalendar === "undefined") {
            console.error("FullCalendar is not defined. Ensure it is loaded before dashboard.js");
            return;
        }

        const calendarEl = document.getElementById("calendar");
        if (!calendarEl) {
            console.warn("#calendar element not found in DOM. Calendar can only be initialized when DOM contains #calendar.");
            return;
        }

        // build instance
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: "dayGridMonth",
            selectable: true,
            editable: true,
            eventDurationEditable: true,
            height: "auto",
            headerToolbar: {
                left: "prev,next today",
                center: "title",
                right: ""
            },
            events: window.user_periods || [],

            //when user clicks on a specific day
            dateClick: function(info) {
                const dateStr = info.dateStr;
                const panel = document.getElementById("day-info-panel");
                const noEventDiv = document.getElementById("day-no-event");
                const hasEventDiv = document.getElementById("day-has-event");

                //reset: hide all inner content
                noEventDiv.classList.add("hidden");
                hasEventDiv.classList.add("hidden");

                // show panel
                panel.classList.add("visible");
                panel.classList.remove("hidden");
                document.getElementById("day-info-date").textContent = dateStr;

                // find events for that day
                const events = calendar.getEvents();
                const clickedDate = new Date(dateStr);

                const eventForDay = events.find(ev => {
                    const start = new Date(ev.start);
                    const end = new Date(ev.end || ev.start);
                    end.setDate(end.getDate() - 1);
                    return clickedDate >= start && clickedDate <= end;
                });

                if (!eventForDay) {
                    // NO event
                    noEventDiv.classList.remove("hidden");

                    //log period option
                    document.getElementById("btn-log-period").onclick = function () {
                        fetch("/api/periods", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                period_start: dateStr,
                                period_end: dateStr
                            })
                        })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success && data.id) {
                                calendar.addEvent({
                                    id: data.id,
                                    title: "Period",
                                    start: dateStr,
                                    end: dateStr,
                                    allDay: true
                                });
                                alert("Period logged.");
                                panel.classList.remove("visible"); // hide after logging
                                panel.classList.add("hidden");
                            } else {
                                alert("Failed to log period.");
                            }
                        });
                    };

                } else {
                    // HAS event
                    hasEventDiv.classList.remove("hidden");

                    document.getElementById("event-start").textContent = eventForDay.startStr;
                    document.getElementById("event-end").textContent = eventForDay.endStr;

                    // edit period
                    document.getElementById("btn-edit-period").onclick = function () {
                        const newStart = prompt("New start date:", eventForDay.startStr);
                        if (!newStart) return;

                        const newEnd = prompt("New end date:", eventForDay.endStr);
                        if (!newEnd) return;

                        eventForDay.setStart(newStart);
                        eventForDay.setEnd(newEnd);

                        fetch('/api/periods/${eventForDay.id}', {
                            method: "PUT",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                period_start: newStart,
                                period_end: newEnd
                            })
                        })
                        .then(r => r.json())
                        .then(data => {
                            if (!data.success) alert("Failed to update period.");
                            else {
                                panel.classList.remove("visible"); //hide after edit
                                panel.classList.add("hidden");
                            }
                        });
                    };

                    // delete period
                    document.getElementById("btn-delete-period").onclick = function () {
                        if (!confirm("Delete this period?")) return;

                        fetch('/api/periods/${eventForDay.id}', { method: "DELETE" })
                        .then(r => r.json())
                        .then(data => {
                            if (data.success) {
                                eventForDay.remove();
                                panel.classList.remove("visible");
                                panel.classList.add("hidden");
                                alert("Period deleted.");
                            } else {
                                alert("Failed to delete period.");
                            }
                        });
                    };
                }
            }
        });

        // render calendar
        calendar.render();
        calendarRendered = true;
        console.log("Calendar initialized and rendered.");
    })();

    tabs.forEach(tab => {
        tab.addEventListener("click", (e) => {
            e.preventDefault();
            const target = tab.getAttribute("data-target");

            // handle logout tab
            if (target === "logout-tab" && logoutForm) {
                logoutForm.submit();
                return;
            }

            // Deactivate active tab
            if (tab.classList.contains("active")) {
                tab.classList.remove("active");
                const targetElement = document.getElementById(target);
                if (targetElement) targetElement.classList.remove("active");
                if (log_period_btn) log_period_btn.style.display = "block";
                return;
            }

            // Activate clicked tab
            tabs.forEach(t => t.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));

            tab.classList.add("active");

            const targetElement = document.getElementById(target);
            if (targetElement) targetElement.classList.add("active");

            if (log_period_btn) log_period_btn.style.display = "none";

            if (target === "calendar-tab" && calendarRendered && calendar) {
                setTimeout(() => {
                    try {
                        calendar.updateSize();
                    } catch (err) {
                        console.warn("calendar.updateSize failed", err);
                    }
                }, 50);
            }
        });
    });

    if (typeof FullCalendar === "undefined") {
        console.error("FullCalendar is undefined at DOMContentLoaded. Ensure this script loads AFTER FullCalendar, e.g. include FullCalendar <script> before dashboard.js in the template");
    }

    // to deselect
    document.addEventListener("click", function(e) {
        const panel = document.getElementById("day-info-panel");
        if (!panel.contains(e.target) && !e.target.closest(".fc-daygrid-day")) {
            panel.classList.remove("visible");
            panel.classList.add("hidden");
        }
    });
});
