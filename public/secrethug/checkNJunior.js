function forLoginData() {
	return new Promise((resolve) => {
		const btn = document.getElementById("submitLogin");

		const handler = () => {
			const email = document.getElementById("emailInp").value.trim();
			const studentIdRaw = document.getElementById("studentId").value.trim();

			const emailRegex = /^[a-zA-Z0-9]+\.[a-zA-Z0-9]{3}$/;
			const studentIdNum = Number(studentIdRaw);

			const isEmailValid = emailRegex.test(email);
			const isStudentIdValid =
				Number.isInteger(studentIdNum) &&
				studentIdNum >= 6780000 &&
				studentIdNum <= 6789999;

			if (!isEmailValid || !isStudentIdValid) {
				Toastify({
					text: "Enter a valid login credential",
					duration: 3000,
					backgroundColor: "#e53e3e",
					gravity: "bottom",
					position: "center"
				}).showToast();

				resolve(null);
				cleanup();
				return;
			}

			resolve({
				email: `${email}`,
				studentId: studentIdRaw
			});

			cleanup();
		};

		const cleanup = () => {
			btn.removeEventListener("click", handler);
		};

		btn.addEventListener("click", handler);
	});
}

function escxss(str) {
	return str.replace(/[&<>"']/g, (match) => ({
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#39;',
	}[match]));
}

function createNcard(name, studentid, major, instagram) {
	let card = `
	<div class="card">
		<div id="id">${escxss(studentid.toString())}</div>
		<div id="n-name">${escxss(name)}</div>
		<div id="n-major">${escxss(major)}</div>
		<div class="social-row" style="display: flex; align-items: center; align-content: center; gap: 6px;">
		<div class="ig-logo-circle"><i class="fa-brands fa-instagram"></i></div>
		<div id="n-ig" style="user-select: text;">${escxss(instagram)}</div>
		</div>
	</div>`
	document.getElementById("container").innerHTML+=card;
	console.log("DONE");
}

async function main() {

	let data = null;
	let qresult = null;
	while (true) {
		data = await forLoginData();
		// validate
		if (data !== null) {
			qresult = await post("/api/secrethug/checkncode", {id: data["studentId"], email: data["email"]})
			console.log(qresult);
			if (qresult.status === "OK") {break;}
			if (qresult.status === "REJ") {
				Toastify({
					text: "Invalid Login Credential ("+qresult.reason+")",
					duration: 2500,
					escapeMarkup: false,
					backgroundColor: "#e53e3e",
					gravity: "bottom",
					position: "center"
				}).showToast();
				setTimeout(()=>{
					Toastify({
					text: `If the issue persists,<br>contact us via our official Instagram.<br><small><small><i>(Click here to visit our Instagram)</i></small></small>`,
					escapeMarkup: false,
					duration: 4000,
					close: false,
					gravity: "bottom",
					position: "center",
					backgroundColor: "#e53e3e",
					onClick: () => window.open('https://www.instagram.com/chamomile.cmm678/', '_blank')
				}).showToast();}, 1250);
				
			} else if (qresult.status === "FAILED") {
				Toastify({
					text: "Invalid Login Credential ("+qresult.reason+")",
					duration: 2500,
					escapeMarkup: false,
					backgroundColor: "#e53e3e",
					gravity: "bottom",
					position: "center"
				}).showToast();
				setTimeout(()=>{
				Toastify({
					text: `If you believe this is a mistake,<br>Contact us via our official Instagram.<br><small><small><i>(Click here to visit our Instagram)</i></small></small>`,
					escapeMarkup: false,
					duration: 4000,
					close: false,
					gravity: "bottom",
					position: "center",
					backgroundColor: "#e53e3e",
					onClick: () => window.open('https://www.instagram.com/chamomile.cmm678/', '_blank')
				}).showToast();}, 1250);
			}
			
		}
	}
	let modal = document.getElementById("loginmodal");
	modal.classList.add("fadeoutnow");
	setTimeout(()=>{
		modal.style.opacity = 0;
		modal.style.display = "none"
	}, 270)
	console.log(data, "HETYHKEGYHUEAGJKEGEGKJEGKEGLK");
	for (let i = 0; i < qresult.data.length; i++) {
		let [id, name, nick, major, insta] = qresult.data[i];
		console.log("MAKING CARD FOR", id)
		createNcard("N'"+nick, id, major, insta);
	}
}

main()