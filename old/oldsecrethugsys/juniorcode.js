


if (!isLoggedIn()) {
  redirect_to_login();
}


const loadingToast = Toastify({
    text: "Loading data...",
    duration: -1,
    close: false,
    gravity: "bottom",
    position: "center",
    backgroundColor: "#6464649a"
});
loadingToast.showToast();
let handlecount = 0;
function buildCard(name, nickname, instagram, studentid) {
  var card = `
  <div class="nong-card">
    <div class="nong-content">
    <div class="nong-main">
      <h2 class="nong-name">N'${nickname}</h2>
      <span class="nong-description">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M240 192C240 147.8 275.8 112 320 112C364.2 112 400 147.8 400 192C400 236.2 364.2 272 320 272C275.8 272 240 236.2 240 192zM448 192C448 121.3 390.7 64 320 64C249.3 64 192 121.3 192 192C192 262.7 249.3 320 320 320C390.7 320 448 262.7 448 192zM144 544C144 473.3 201.3 416 272 416L368 416C438.7 416 496 473.3 496 544L496 552C496 565.3 506.7 576 520 576C533.3 576 544 565.3 544 552L544 544C544 446.8 465.2 368 368 368L272 368C174.8 368 96 446.8 96 544L96 552C96 565.3 106.7 576 120 576C133.3 576 144 565.3 144 552L144 544z"/></svg> ${name} <small><small>(ID : ${studentid})</small></small><br>
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-instagram" viewBox="0 0 16 16">
  <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.9 3.9 0 0 0-1.417.923A3.9 3.9 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.9 3.9 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.9 3.9 0 0 0-.923-1.417A3.9 3.9 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599s.453.546.598.92c.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.5 2.5 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.5 2.5 0 0 1-.92-.598 2.5 2.5 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233s.008-2.388.046-3.231c.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92s.546-.453.92-.598c.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92m-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217m0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334"/>
</svg> <span class="instagramhandle" id="insta-handle-${handlecount}">${instagram} <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" class="copysvg"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M480 400L288 400C279.2 400 272 392.8 272 384L272 128C272 119.2 279.2 112 288 112L421.5 112C425.7 112 429.8 113.7 432.8 116.7L491.3 175.2C494.3 178.2 496 182.3 496 186.5L496 384C496 392.8 488.8 400 480 400zM288 448L480 448C515.3 448 544 419.3 544 384L544 186.5C544 169.5 537.3 153.2 525.3 141.2L466.7 82.7C454.7 70.7 438.5 64 421.5 64L288 64C252.7 64 224 92.7 224 128L224 384C224 419.3 252.7 448 288 448zM160 192C124.7 192 96 220.7 96 256L96 512C96 547.3 124.7 576 160 576L352 576C387.3 576 416 547.3 416 512L416 496L368 496L368 512C368 520.8 360.8 528 352 528L160 528C151.2 528 144 520.8 144 512L144 256C144 247.2 151.2 240 160 240L176 240L176 192L160 192z"/></svg></span><br>
      </p>
    </div>
    </div>
  </div>
  `;

  document.getElementById('scroll-container').insertAdjacentHTML('beforeend', card);
  document.getElementById(`insta-handle-${handlecount}`).addEventListener('click', async function() {
    console.log('Span clicked!', instagram);
    await navigator.clipboard.writeText(instagram);
    Toastify({
      text: "Copied!",
      duration: 1000,
      close: false,
      gravity: "bottom",
      position: "center",
      backgroundColor: "#00ff009a"
    }).showToast();
  });

  handlecount+=1;
  return card;
}

fetch("/secrethugSGETJ", {method: "POST", credentials: "same-origin"}).then((res)=>{
	if (!res.ok) throw new Error(res.reason);
  return res.json();
}).then((res) => {

  if (res.success === false) {
    deleteCookie("session_id");
    if (res.reason === "Expired token") {
      redirect_to_login(["expired=expired"]);
    } else {
      redirect_to_login();
    }
    return;
  }
  
  if (res.length > 0) {
    res.forEach((thisdude) => {
      buildCard(thisdude.name, thisdude.nick, thisdude.insta, thisdude.id)
    })
  } else {
    Toastify({
      text: `<big>You currently have no N'Junior assigned</big>`,
      escapeMarkup: false,
      duration: -1,
      close: false,
      gravity: "bottom",
      position: "center",
      backgroundColor: "#ff00009a",
    }).showToast();
    Toastify({
      text: `If you believe this is a mistake,<br>
      Contact us via our official Instagram.<br>
      <small><small><i>(Click here to visit our Instagram)</i></small></small>`,
      escapeMarkup: false,
      duration: -1,
      close: false,
      gravity: "bottom",
      position: "center",
      backgroundColor: "#6464649a",
      onClick: () => {
        window.open('https://www.instagram.com/chamomile.cmm678/', '_blank');
      },
    }).showToast();
  }

  Toastify({
    text: `Retrieved!`,
    duration: 1000,
    close: false,
    gravity: "bottom",
    position: "center",
    backgroundColor: "#00ff009a"
  }).showToast();
}).catch ((err) => {
  console.error(err);
  Toastify({
    text: "Server Error: " + err.message,
    duration: 3000,
    close: false,
    gravity: "bottom",
    position: "center",
    backgroundColor: "#ff00009a"
  }).showToast();
  deleteCookie("session_id");
  setTimeout(() => redirect_to_login(), 3000);
}).finally(() => {
  loadingToast.hideToast();
})

