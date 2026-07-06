const vineboom = new Audio("chamomimi.mp3");
document.getElementById("logoimg").addEventListener('click', function() {
  vineboom.currentTime = 0;
  vineboom.play();
});

function getCookie(query) {
  const cookie_now = document.cookie.split("; ");
  for (let i = 0; i < cookie_now.length; i++) {
    let str = cookie_now[i].split("=");
    let key = str[0];
    let value = str[1];
    if (key === query) {
      if (!isNaN(Number(value))) {
        value = Number(value);
      }
      return value;
    }
  }
  return null;
}

function clearSession() {
  const cookiesToClear = ["session_id", "student_id", "email"];
  cookiesToClear.forEach(cookie => {
    document.cookie = cookie + "='';expires=Thu, 01 Jan 1970 00:00:01 GMT";
  });
  storedCookie = "";
}

function cap(st) {
  return st.charAt(0).toUpperCase() + st.slice(1);
}

let storedCookie = getCookie("session_id");
let email = getCookie("email");
let loggedin = true;

if (storedCookie && storedCookie !== "" && email && email !== "") {
  let studentid = getCookie("student_id");
  if (!studentid || studentid === "") {
    window.location.href = "./idbind";
  } else {
    document.getElementById("account_button").innerText = "HI! " + email.split(".")[0].toUpperCase();
    Toastify({
      text: "Welcome, " + cap(email.split(".")[0]) + "!",
      duration: 2000,
      close: false,
      stopOnFocus: false,
      gravity: "bottom",
      position: "center",
      backgroundColor: "#6464649a",
    }).showToast();
  }
} else {
  Toastify({
    text: "You are not logged in.",
    duration: 1200,
    close: false,
    gravity: "bottom",
    position: "center",
    backgroundColor: "#6464649a"
  }).showToast();
  clearSession();
}

const popup = new Popup({
  id: "logout",
  title: "Log out confirmation",
  content: `Do you wish to log out?
      {btn-accept}[Yes]   {btn-refuse}[No]`,
  allowClose: false,
  loadCallback: function() {
    document.querySelector(".refuse").onclick = () => {
      popup.hide();
    };
    document.querySelector(".accept").onclick = () => {
      clearSession();
      Toastify({
        text: "You have been logged out.",
        duration: 1200,
        close: false,
        stopOnFocus: false,
        gravity: "bottom",
        position: "center",
        backgroundColor: "#6464649a"
      }).showToast();
      popup.hide();
      document.getElementById("account_button").innerText = "ACCOUNT";
    };
  }
});

/*document.getElementById("account_button").addEventListener("click", function() {
  if (!storedCookie || storedCookie === "") {
    window.location.href = "login";
  } else {
    popup.show();
  }
});*/