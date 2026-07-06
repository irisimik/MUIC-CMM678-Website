

// logging in
/*
      <input type="text" id="emailInp" class="modalinputbox" style="margin-top: 0.1rem;" placeholder="john.doe@student.mahidol.edu">
      <p>Your student ID</p>
      <input type="text" id="studentId" class="modalinputbox" style="margin-top: 0.1rem;" placeholder="678xxxx"></input>
*/

let loggedin = false;
let usremail = null;
let usrid = null;

async function letlogin() {
  const studentid = Number(document.getElementById("studentId").value.trim());
    if (!studentid || studentid > 6889999 || studentid < 6780000) {
      Toastify({
        text: "Enter a valid login credential",
        duration: 3000,
        backgroundColor: "#e53e3e",
        gravity: "bottom",
        position: "center"
      }).showToast();
      return;
    }
    let email = document.getElementById("emailInp").value.trim().toLowerCase();
    if (!email) {
      Toastify({
        text: "Enter a valid email",
        duration: 3000,
        backgroundColor: "#e53e3e",
        gravity: "bottom",
        position: "center"
      }).showToast();
      return;
    }

    email += "@student.mahidol.edu"
    
    let waittoast = Toastify({
        text: "Logging you in...",
        duration: 3000,
        backgroundColor: "#0e0e0e",
        gravity: "bottom",
        position: "center"
      });
    waittoast.showToast();

    const res = await fetch("/sercretauth", {"method": "POST", "Content-Type": "application/json", "body": JSON.stringify({id:studentid, email:email})});
    waittoast.hideToast();
    if (!res.ok) {
      Toastify({
        text: "Server Error, Refresh the page and try again (1)",
        duration: 3000,
        backgroundColor: "#e53e3e",
        gravity: "bottom",
        position: "center"
      }).showToast();
      return;
    }
    const result = (await res.json()).auth;
    if (!result) {
      Toastify({
        text: "Authentication failed: Invalid credential.",
        duration: 3000,
        backgroundColor: "#e53e3e",
        gravity: "bottom",
        position: "center"
      }).showToast();
      return;
    }

    document.getElementById("loginmodal").style.display = "none";
    usremail = email;
    usrid = studentid;
    loggedin = true;


    onLoggedIn();
}

document.getElementById("studentId").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    letlogin();
  }
});

document.getElementById("submitLogin").addEventListener("click", () => {
  console.log("login")
  letlogin();
})

function seniorthing() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('image-preview');
  const removeBtn = document.getElementById('remove-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const modal = document.getElementById("nongPrompt");
  modal.style.display = "none";
  dropZone.classList.remove('preview-hidden');

  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  ['dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, () => dropZone.classList.remove('dragover'));
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    handleFiles(files);
  });

  fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
  });

  async function compressImage(file, maxSizeMB = 5) {
    const maxSize = maxSizeMB * 1024 * 1024;

    const img = await createImageBitmap(file);

    const canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    let quality = 0.9;
    let blob;

    do {
      blob = await new Promise(resolve =>
        canvas.toBlob(resolve, "image/jpeg", quality)
      );
      quality -= 0.05;
    } while (blob.size > maxSize && quality > 0.1);

    return blob;
  } 

  function handleFiles(files) {
    const file = files[0];
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];

    if (file && allowedTypes.includes(file.type)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewContainer.classList.remove('preview-hidden');
        dropZone.classList.add('preview-hidden');
      };
      reader.readAsDataURL(file);
    } else {
      Toastify({
        text: "Please upload a valid JPG, PNG, or WEBP image.",
        duration: 3000,
        backgroundColor: "#e53e3e",
      }).showToast();
    }
  }
  

  function clearstuff() {
    fileInput.value = '';
    previewContainer.classList.add('preview-hidden');
    dropZone.classList.remove('preview-hidden');
  }
  removeBtn.addEventListener('click', () => {
    clearstuff();
  });

  modal.style.display = "none";
  async function uploadimg(targetId, note) {
    const file = fileInput.files[0];
    
    if (!file) {
      Toastify({ text: "Please select a file first", backgroundColor: "#e53e3e" }).showToast();
      return;
    }

    const formData = new FormData();
    const compressedBlob = await compressImage(file, 5);

    formData.append('giftImage', compressedBlob);
    // TODO : implement student id selection thingy or smth idk idgaf

    formData.append('targetId', targetId);
    
    formData.append('note', note);
    formData.append('email', usremail);
    formData.append('id', usrid.toString());
    
    try {
      uploadBtn.innerText = "Uploading...";
      uploadBtn.style.opacity = "0.7";
      uploadBtn.disabled = true;
      const response = await fetch('/uploadgift', {
        method: 'POST',
        body: formData,
        credentials: 'omit'
      });

      if (response.ok) {
        Toastify({
          text: "Gift uploaded successfully! 🎁",
          backgroundColor: "var(--primary-green)",
          close: false,
          gravity: "bottom",
          position: "center",
        }).showToast();
        confetti({
          particleCount: 150,
          spread: 90,
          origin: { y: 1 },
          zIndex: 999999
        });
        const id = (await response.json()).giftid;
        document.getElementById("giftidtext").innerHTML="Your gift ID is <strong>"+id+"</strong>";
        document.getElementById("giftIdDisp").style.display = "flex";
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error("Error:", error);
      Toastify({
        text: "Error uploading image. Please try again.",
        backgroundColor: "#e53e3e",
        close: false,
        gravity: "bottom",
        position: "center",
      }).showToast();
    } finally {
      uploadBtn.innerText = "Submit Photo";
      uploadBtn.style.opacity = "1";
      uploadBtn.disabled = false;
      clearstuff();
    }
  }

  function getNote() {
    return new Promise((resolve) => {
      const modal = document.getElementById("notePrompt");
      const input = document.getElementById("noteInput");
      const button = document.getElementById("submitNote");

      modal.style.display = "flex";
      input.value = "";
      input.focus();

      const submit = () => {
        modal.style.display = "none";
        button.removeEventListener("click", submit);
        input.removeEventListener("keydown", onKeyDown);
        resolve(input.value);
      };

      const onKeyDown = (e) => {
        if (e.key === "Enter") submit();
      };

      button.addEventListener("click", submit);
      input.addEventListener("keydown", onKeyDown);
    });
  }

  uploadBtn.addEventListener('click', async () => {
    modal.style.display = "flex";
    let nonglist = [];
    try {
      nonglist = await (await fetch("/getgiftrecipientlist", {"method": "POST", 'credentials': 'omit', 'Content-Type': 'application/json', "body": JSON.stringify({email:usremail,id:usrid})})).json();
    } catch(error) {
      console.error("Error:", error);
      Toastify({
        text: `Error fetching your N'juniors data.
        Please refresh the page and try again.
        <small>(${error})</small>`,
        backgroundColor: "#e53e3e",
        close: false,
        escapeMarkup: false,
        gravity: "bottom",
        position: "center",
      }).showToast();
    }
    const parent = document.getElementById("cardsContainer");
    parent.innerHTML = '';
    let id = 0;
    let thisclicked = false;
    for (let nongdata of nonglist.nongdatas) {
      let disabled = false;
      if (nonglist.gifted.includes(Number(nongdata.id))) {
        disabled = true;
      }
      let card = `
      <a class="recipient-card ${disabled ? "disabled" : ""}" id="nongti${id}">
        <span class="name">N'${nongdata.nick} <small><small>(${nongdata.id})</small></small></span>
        ${disabled?"<span class=\"note\">Only one gift can be deposited at a time.<br>Please wait until your N'junior collect the gift.</span>":""}
      </a>`

      parent.insertAdjacentHTML("beforeend", card);
      console.log(document.getElementById("nongti"+id));
      document.getElementById("nongti"+id).addEventListener("click", async () => {
        modal.style.display = "none";

        if (thisclicked) {return;}


        thisclicked = true;
        let toast = Toastify({
          text: `Uploading...`,
          backgroundColor: "#3e3e3e",
          close: false,
          escapeMarkup: false,
          duration: -1,
          gravity: "bottom",
          position: "center",
        });
        let note = await getNote();
        console.log("note is", note);

        toast.showToast();
        await uploadimg(nongdata.id,note);
        toast.hideToast();
        
        parent.innerHTML = "";
      });
      id+=1;
    }
  });
}


let forcejndisp = false;
async function juniorthing() {
  document.getElementById('drop-zone').style.display = "none";
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('image-preview');
  document.getElementById("remove-btn").style.display = "none";
  document.getElementById("upload-btn").style.display = "none";
  document.getElementById("redeem-btn").classList.remove("preview-hidden");
  
  previewImage.src = "/tickets/ripple.gif";
  previewContainer.classList.remove('preview-hidden');
  async function getgiftdata() {
    const res = await fetch("/checkgift", {
      method: "POST", 
      headers: {'Content-Type': 'application/json'}, 
      credentials: 'omit',
      body: JSON.stringify({email: usremail, id: usrid})
    });
    if (!res.ok) {
      return {success: false};
    }
    return res.json();
  }
  
  let giftfound = false;
  let giftid = null;
  async function updatePage() {
    const giftdata = await getgiftdata();
    if (giftdata.success) {
      const d = giftdata.data; // giftid, giftimg, note
      giftid = d[0];
      document.getElementById("image-preview").src = "/uploads/"+d[1];
      const note = d[2];
      giftfound = true;
      let toast = Toastify({
        text: `<big><big><strong>Your gift ID is ${giftid}</strong></big></big><br>
        Please show this page to our CMM staff to collect your gift.<br>
        After you recieved your gift, <br>please press the redeem button to view the note sent by your P'Senior`,
        close: false,
        gravity: "top",
        duration: -1,
        position: "center",
        escapeMarkup: false,
      });
      toast.showToast();
      document.getElementById("redeem-btn").classList.remove("redeemloading")
      document.getElementById("redeem-btn").addEventListener("click", ()=>{
        if (!giftid) {
          return;
        }
        toast.hideToast();
        // redeem
        fetch("/redeemgift",{method: 'POST', headers: {'Content-Type': 'application/json',credentials: 'omit'}, body: JSON.stringify({giftid: giftid, email: usremail, id: usrid})});
        giftid = null;
        document.getElementById("notedisp").innerText = note;
        document.getElementById("noteRedeem").style.display = "flex";
        Toastify({
          text: `🎁 Gift redeemed! Enjoy!`,
          backgroundColor: "var(--primary-green)",
          close: false,
          gravity: "bottom",
          position: "center",
        }).showToast();
        confetti({
          particleCount: 150,
          spread: 90,
          origin: { y: 1 },
          zIndex: 999999
        });
        document.getElementById("image-preview").src = ""
      })
      
    } else {
      console.log("no gift");
      document.getElementById("image-preview").src = "/uploads/nogift.jpg"
    }
  }
  
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && !giftfound && loggedin) {
      updatePage();
    }
  });
  updatePage();
}

function onLoggedIn() {
  if (usrid < 6880000 && !forcejndisp) {
    seniorthing();
  } else {
    juniorthing();
  }
}