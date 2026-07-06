

const modal = document.getElementById("idPrompt");
const input = document.getElementById("studentIdInput");
const submit = document.getElementById("submitId");

const datamap = {"2":["/rubnong/assets/G2.png",[[65.74,75.5,13,1.5],[25.74,75.5,13,1.5]],["https://line.me/ti/g/NPFffKgAnE","https://www.instagram.com/g.2marvelous?igsh=cXZlbGowa3Zicjdi&utm_source=qr"],"w"],"6":["/rubnong/assets/G6.jpg",[[66.44,63.125,14.225,1.58],[20.647,63.125,13.055,1.58]],["https://line.me/ti/g/Mmn6J7ZuBk","https://www.instagram.com/g6_sixpoints.forravenclaw?igsh=MWMzMmVpODZleTE2eg%3D%3D&utm_source=qr"],"b"],"7":["/rubnong/assets/G7.jpg",[[44,69.48,12,1.5],[43.5,93.25,13,1.5]],["https://line.me/ti/g/s_MVzhVmKR","https://www.instagram.com/g7_seven.yatchs/"],"w"],"8":["/rubnong/assets/G8.JPG",[[44,55.3,12,2.06],[44,85,12,2.06]],["https://line.me/ti/g/zq6Vrqk8E6","https://www.instagram.com/g8.untangled?igsh=MWU5aTAzcXQ0cndtZg%3D%3D&utm_source=qr"],"b"],"14":["/rubnong/assets/G14.jpeg",[[43.5,88,15,1.6],[43.5,91,15,1.6]],["https://line.me/ti/g/Q3SLUqZHXa","https://www.instagram.com/g14_kipromwiset?igsh=aWhjbTJsZDVkaHU4&utm_source=qr"],"w"],"22":["/rubnong/assets/G22.png",[[22.5,74.25,12.2,1.5],[60.763,74.25,15,1.5]],["https://line.me/ti/g/q7C9rDKQw6","https://www.instagram.com/the22neverpan?igsh=MTc2ZTBlODhmdTdo&utm_source=qr"],"b"],"40":["/rubnong/assets/G40.png",[[31.54,78.3,12.25,1.5],[60.22,78.3,12.25,1.5]],["https://line.me/ti/g/mcUdcj8Dqj","https://www.instagram.com/g40.yangjaew?igsh=MXZ3Z3Rjdzk5MnI1bQ%3D%3D&utm_source=qr"],"b"],"67":["/rubnong/assets/G67.png",[[17.5,96,15,1.5],[67.5,96,15,1.5]],["https://line.me/ti/g/4G4tRTFZAT","https://www.instagram.com/g67.thewickedwitch?igsh=MWZjcTRqZHh6ZXh6dA%3D%3D&utm_source=qr"],"w"],
	"99":[
		"/rubnong/assets/G99.png",
		[[15.925925925925927, 41.354166666666664, 12, 1.5], [72.074074074074, 39.4166666666664, 12.0, 1.5]],
		["https://line.me/ti/g/9d7YLzZpDD", "https://www.instagram.com/g99_99thundershine?igsh=aWp2NTVyYm52N2Uz&utm_source=qr"],
		"w"
	],
	"TMP":[
		"/rubnong/assets/CMMticket.png",
		[[1500.925925925925927, 41.354166666666664, 12, 1.5], [7200.074074074074, 39.4166666666664, 12.0, 1.5]],
		["https://line.me/ti/g/9d7YLzZpDD", "https://www.instagram.com/g99_99thundershine?igsh=aWp2NTVyYm52N2Uz&utm_source=qr"],
		"w"
	]
};

let inputawaitid = 0;
function waitForInput() {
	return new Promise((resolve) => {
		inputawaitid += 1;
		const curawait = inputawaitid;

		console.log("New promise for login");
		modal.style.display = "flex";
		input.focus();
		input.value = "";
		const finish = (value) => {
			modal.style.display = "none";
			cleanup();
			resolve(value);
		};
		const handleSubmit = () => {
			if (curawait !== inputawaitid) {
				cleanup();
				return;
			}
			const value = Number(input.value.trim());
			if (value && (value >= 6880000 && value < 6890000) || (value === 6781381)) {// || (datamap[value.toString()])) {
				finish(value);
			} else {
				Toastify({
					text: "Enter a valid ID",
					duration: 1500,
					close: false,
					gravity: "top",
					position: "center",
					backgroundColor: "#ff00009a"
				}).showToast();
			}
		};
		const handleEnter = (e) => {
			if (e.key === "Enter") handleSubmit();
		};
		const cleanup = () => {
			submit.removeEventListener("click", handleSubmit);
			input.removeEventListener("keydown", handleEnter);
		};
		submit.addEventListener("click", handleSubmit);
		input.addEventListener("keydown", handleEnter);
	});
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const crack = document.getElementById("crackOverlay");
const flash = document.getElementById("flashOverlay");


function fitText(button) {
	let fontSize = 16;
	button.style.fontSize = fontSize + "px";

	while (button.scrollWidth > button.clientWidth && fontSize > 0) {
		fontSize--;
		button.style.fontSize = fontSize + "px";
		console.log(fontSize);
	}
}
function showTicket(imageUrl, positionsArray, urlsArray, tc="w", colors=["rgba(0,0,0,0)", "rgba(0,0,0,0)"], labelsArray=["Click To Join", "Click To View"]) {
	const ticket = document.getElementById("ticket");

	const buttonsHTML = positionsArray.map((pos, index) => {
		const [left, top, width, height] = pos;
		const url = urlsArray[index] || "#";
		const c = colors[index];
		const label = labelsArray[index] || "click me";
		const textcolor = tc === "w" ? "cyan"	: "blue";

		return `
			<button class="imgbutton"
				style="
					left: ${left}%;
					top: ${top}%;
					width: ${width}%;
					height: ${height}%;
					background-color: ${c};
					text-decoration: underline;
					color: ${textcolor};
				"
				onclick="window.location.href='${url}'"
			>
				${label}
			</button>
		`;
	}).join("");

	ticket.innerHTML = `
		<div class="img-wrapper">
			<img src="${imageUrl}" alt="ticket">
			${buttonsHTML}
		</div>
	`;

	requestAnimationFrame(() => {
		ticket.classList.add("ticketenable");
	});
}

function hideTicket() {
	const ticket = document.getElementById("ticket");
	ticket.classList.remove("ticketenable");
	setTimeout(() => {
		ticket.innerHTML = "";
	}, 400);
}

const nogroupToast1 = Toastify({
	text: `If you believe this is a mistake,<br>Contact us via our official Instagram.<br><small><small><i>(Click here to visit our Instagram)</i></small></small>`,
	escapeMarkup: false,
	duration: -1,
	close: false,
	gravity: "bottom",
	position: "center",
	backgroundColor: "#6464649a",
	onClick: () => window.open('https://www.instagram.com/chamomile.cmm678/', '_blank')
});
const nogroupToast2 = Toastify({
	text: `You do not have Rubnong group.`,
	escapeMarkup: false,
	duration: -1,
	close: false,
	gravity: "center",
	position: "center",
	backgroundColor: "#ff00009a",
	onClick: () => window.location.reload()
});
async function main() {
	let modal = document.getElementById("idPrompt") 
	modal.style.display = "flex";
	id = await waitForInput();

	modal.style.display = "none";

	console.log(id);
	document.body.classList.add("fade-out");
	const wk = document.getElementById("walker")

	wk.classList.remove("animoff");
	wk.classList.add("animwalk");
	await sleep(1000); 

	let groupid;
	console.log(id);
	if (datamap[id.toString()]) {
		groupid = id.toString();
	} else {
		groupid = await post("/api/rubnong/checkidngroup", {id: id});
		if (!groupid || !groupid["group"] || groupid["group"] === "n") {
			await get("/rubnong/assets/cmshock.png");
			wk.classList.remove("animwalk");
			wk.classList.add("animshock");
			document.body.classList.remove("fade-out");
			nogroupToast2.showToast();
			nogroupToast1.showToast();
			return;
			// indicate error
		}
		groupid = groupid["group"].toString();

		// handle id
	}

	let data = datamap[groupid];
	if (!data) {
		await get("/rubnong/assets/cmshock.png");
		wk.classList.remove("animwalk");
		wk.classList.add("animshock");
		document.body.classList.remove("fade-out");
		nogroupToast1.showToast();
		return;
	}

	let [asseturl, pos, url, mode] = data;

	modal.style.display = "none"
	let imgpromise = get(asseturl);
	//await get("/rubnong/assets/G8.JPG");
	
	flash.classList.add("flash-active");
	await sleep(2400);
	await imgpromise;
	console.log(groupid);
	
	showTicket(
		asseturl, 
		pos,
		url,
		mode
	)
	document.getElementById("shining").classList.add("shine");
	document.body.classList.remove("fade-out");
	await sleep(500);
	flash.classList.remove("flash-active");
	flash.classList.add("flash-fadeout");
	
	
}

main();