

  const root = document.getElementById("supercool-login-root");
	console.log(root)

  root.innerHTML = `
    <div id="supercool-login-backdrop">
      <div id="supercool-login-wrapper">
        <div id="supercool-login-modal">
          <div id="supercool-login-title">
            Login
          </div>
          <div id="supercool-login-subtitle">
 
          </div>

          <form id="supercool-login-form">
            <div class="supercool-login-group">
              <input type="email" id="supercool-login-email" placeholder="Email" required/>
            </div>

            <div class="supercool-login-group">
              <input type="text" id="supercool-login-password" placeholder="Student ID" required/>
            </div>

            <button type="submit" id="supercool-login-submit">
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  `;

  const backdrop = document.getElementById("supercool-login-backdrop");

  const form = document.getElementById("supercool-login-form");
  const closeButton = document.getElementById("supercool-login-close");
  const emailInput = document.getElementById("supercool-login-email");
  const passwordInput = document.getElementById("supercool-login-password");

  let resolver = null;

  openlogin = function () {

    backdrop.classList.add("supercool-login-active");

    emailInput.value = "";
    passwordInput.value = "";

    setTimeout(() => {
      emailInput.focus();
    }, 50);

    return new Promise((resolve) => {
      resolver = resolve;
    });
  };

  function closeModal() {
    backdrop.classList.remove("supercool-login-active");
  }

  function cancelLogin() {

    closeModal();

    if (resolver) {
      resolver(null);
      resolver = null;
    }
  }


  form.addEventListener("submit", (e) => {

    e.preventDefault();

    const loginInfo = {
      email: emailInput.value,
      password: passwordInput.value
    };

    closeModal();

    if (resolver) {
      resolver(loginInfo);
      resolver = null;
    }

  });
