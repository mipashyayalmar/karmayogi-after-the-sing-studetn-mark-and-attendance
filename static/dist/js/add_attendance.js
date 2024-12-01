function confirmAttendance() {
    // Check if any student is selected before confirming
    var checkboxes = document.querySelectorAll('input[name="student_ids"]:checked');
    if (checkboxes.length === 0) {
        alert("Please select at least one student.");
        return false; // Prevent form submission
    }
    return confirm("Are you sure you want to submit attendance?");
}

// Display message popup
function showMessage() {
    var popup = document.getElementById('message-popup');
    popup.style.display = 'flex';
    
    // Auto-hide success messages after 4 seconds
    if (popup.querySelector('.success-message')) {
        setTimeout(function () {
            popup.style.display = 'none';
        }, 4000); // Change to 4 seconds
    }

    // Auto-hide error messages after 2 seconds
    if (popup.querySelector('.error-message')) {
        setTimeout(function () {
            popup.style.display = 'none';
        }, 3000); // Change to 2 seconds
    }
}

// Trigger message display on page load
document.addEventListener('DOMContentLoaded', showMessage);

// Update current time
function updateCurrentTime() {
    var currentTime = new Date();
    document.getElementById('current-time').innerText = currentTime.toLocaleString();
}
setInterval(updateCurrentTime, 1000); // Update time every second

// Function to update attendance status
function updateAttendanceStatus(checkbox, studentRoll) {
    var status = checkbox.checked ? 1 : 0;
    checkbox.value = status; // Save the current status value

    // No need for additional logic here as the checkbox's value will automatically indicate the attendance status
}

// Select all students
function selectAll() {
    var checkboxes = document.querySelectorAll('input[name="student_ids"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = true;
    });
}

// Mark all students as present
function markAllPresent() {
    var checkboxes = document.querySelectorAll('input[name="student_ids"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = true; // Select all checkboxes
        var attendanceCheckbox = document.querySelector(`input[name="attendance_status_${checkbox.value}"]`);
        attendanceCheckbox.checked = true; // Set attendance status to Present
        updateAttendanceStatus(attendanceCheckbox, checkbox.value); // Update status
    });
}

// Mark all students as absent
function markAllAbsent() {
    var checkboxes = document.querySelectorAll('input[name="student_ids"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = true; // Select all checkboxes
        var attendanceCheckbox = document.querySelector(`input[name="attendance_status_${checkbox.value}"]`);
        attendanceCheckbox.checked = false; // Set attendance status to Absent
        updateAttendanceStatus(attendanceCheckbox, checkbox.value); // Update status
    });
}

// Helper function to update button status
function updateButtonStatus(studentId, isPresent) {
    var button = document.querySelector(`button[data-student="${studentId}"]`);
    if (isPresent) {
        button.setAttribute('data-status', '1');
        button.textContent = 'Present';
        button.classList.remove('btn-outline-danger');
        button.classList.add('btn-outline-success');
    } else {
        button.setAttribute('data-status', '0');
        button.textContent = 'Absent';
        button.classList.remove('btn-outline-success');
        button.classList.add('btn-outline-danger');
    }
}


function confirmAttendance() {
    return confirm("Are you sure you want to submit attendance?");
}

// Display message popup
function showMessage() {
    var popup = document.getElementById('message-popup');
    popup.style.display = 'flex';
    
    // Auto-hide success messages after 4 seconds
    if (popup.querySelector('.success-message')) {
        setTimeout(function () {
            popup.style.display = 'none';
        }, 4000); // Change to 4 seconds
    }

    // Auto-hide error messages after 2 seconds
    if (popup.querySelector('.error-message')) {
        setTimeout(function () {
            popup.style.display = 'none';
        }, 3000); // Change to 2 seconds
    }
}

// Trigger message display on page load
document.addEventListener('DOMContentLoaded', showMessage);

// Update current time
function updateCurrentTime() {
    var currentTime = new Date();
    document.getElementById('current-time').innerText = currentTime.toLocaleString();
}
setInterval(updateCurrentTime, 1000); // Update time every second

// Select all students
function selectAll() {
    var checkboxes = document.querySelectorAll('input[name="student_ids"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = true;
    });
}

// Mark all as present
function markAllPresent() {
    var toggles = document.querySelectorAll('.toggle-label input[type="checkbox"]');
    toggles.forEach(function(toggle) {
        toggle.checked = true;
    });
}

// Mark all as absent
function markAllAbsent() {
    var toggles = document.querySelectorAll('.toggle-label input[type="checkbox"]');
    toggles.forEach(function(toggle) {
        toggle.checked = false;
    });
}

// Update attendance status
function updateAttendanceStatus(checkbox, roll) {
    var status = checkbox.checked ? 'Present' : 'Absent';
    console.log('Attendance for Roll ' + roll + ': ' + status);
}

// Initial current time update
updateCurrentTime();