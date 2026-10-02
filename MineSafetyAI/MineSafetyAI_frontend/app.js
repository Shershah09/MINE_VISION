// ============================================================
// NEXUS ROVER - COMPLETE FRONTEND JAVASCRIPT
// CAMERA + MAP UPGRADED
// ============================================================

const API_URL = "http://127.0.0.1:8000/analyze";

let autoTimer = null;
let emergencyActive = false;

const roverState = {
    x: 42,
    y: 72,
    distance: 125,
    speed: 0.4,
    mapIndex: 0
};

// Coordinates match the tunnel path drawn only inside the Mine Map.
const mineMapPath = [
    [80,430],[105,414],[130,397],[145,375],[140,350],[155,326],
    [180,310],[210,300],[240,292],[270,285],[300,285],[330,292],
    [360,292],[390,270],[410,248],[430,225],[450,200],[470,176],
    [495,150],[520,132],[550,122],[580,123],[610,127],[640,134],
    [670,148],[700,165],[725,183],[745,205],[765,225],[785,242],
    [805,240],[825,215],[842,188],[860,155],[880,125],[910,100]
];


// ============================================================
// PAGE INITIALIZATION
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    setupNavigation();
    setupCameraButtons();
    setupModeButtons();
    setupManualControls();
    setupEmergency();
    setupMapInteractions();
    setupAlertInteractions();

    updateMapRover();
    setMode("automatic");

    createEmergencyModal();

    console.log("NEXUS Rover Dashboard initialized.");
});


// ============================================================
// CLOCK
// ============================================================

function updateClock() {

    const clock = document.getElementById("clock");

    if (clock) {

        clock.textContent =
            new Date().toLocaleTimeString("en-IN", {
                hour12: false
            });

    }

}

setInterval(updateClock, 1000);
updateClock();


// ============================================================
// SIDEBAR NAVIGATION
// ============================================================

function setupNavigation() {

    const navButtons =
        document.querySelectorAll(".nav");

    navButtons.forEach((button) => {

        button.addEventListener("click", () => {

            navButtons.forEach(btn => {
                btn.classList.remove("active");
            });

            button.classList.add("active");

            const text =
                button.innerText.toLowerCase();

            if (text.includes("home")) {

                scrollToPanel(".camera");

            }

            else if (text.includes("map")) {

                scrollToPanel(".map-panel");

            }

            else if (text.includes("camera")) {

                scrollToPanel(".camera");

            }

            else if (text.includes("sensors")) {

                scrollToPanel(".sensors");

            }

            else if (text.includes("rover control")) {

                scrollToPanel(".control");

            }

            else if (text.includes("mission")) {

                showNotification(
                    "Mission Log",
                    "Mission log module is ready."
                );

            }

            else if (text.includes("ai detection")) {

                scrollToPanel(".sensors");

                showNotification(
                    "AI Detection",
                    "Upload an image and run AI analysis."
                );

            }

            else if (text.includes("alerts")) {

                scrollToPanel(".alerts");

            }

            else if (text.includes("settings")) {

                showNotification(
                    "Settings",
                    "Settings panel is available."
                );

            }

        });

    });

}


// ============================================================
// SCROLL TO PANEL
// ============================================================

function scrollToPanel(selector) {

    const panel =
        document.querySelector(selector);

    if (!panel) return;

    panel.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


// ============================================================
// CAMERA SYSTEM
// ============================================================

function setupCameraButtons() {
    const thumbs = document.querySelectorAll(".thumb");
    const cameraView = document.getElementById("cameraView");
    const cameraTitle = document.getElementById("cameraTitle");
    const cameraOverlay = document.getElementById("cameraOverlay");

    const scenes = {
        Front: document.getElementById("frontCameraScene"),
        Rear: document.getElementById("rearCameraScene"),
        Thermal: document.getElementById("thermalCameraScene"),
        LiDAR: document.getElementById("lidarCameraScene")
    };

    thumbs.forEach((thumb) => {
        thumb.addEventListener("click", () => {
            thumbs.forEach(t => t.classList.remove("active"));
            thumb.classList.add("active");

            const mode = thumb.dataset.camera || thumb.textContent.trim();

            Object.values(scenes).forEach(scene => {
                if (scene) scene.classList.add("hidden");
            });

            const selected = scenes[mode];
            if (selected) selected.classList.remove("hidden");

            if (mode === "Front") {
                cameraTitle.innerHTML = '📷 Front Camera - Live Feed <span class="rec">● REC</span>';
                cameraOverlay.textContent = "LIVE AI VISION FEED";
                cameraView.classList.remove("thermal-active", "lidar-active");
            } else if (mode === "Rear") {
                cameraTitle.innerHTML = '📷 Rear Camera - Live Feed <span class="rec">● REC</span>';
                cameraOverlay.textContent = "REAR CAMERA FEED";
                cameraView.classList.remove("thermal-active", "lidar-active");
            } else if (mode === "Thermal") {
                cameraTitle.innerHTML = '🌡 Thermal Camera - Live Feed <span class="rec">● REC</span>';
                cameraOverlay.textContent = "THERMAL IMAGING • TEMPERATURE MAPPING";
                cameraView.classList.add("thermal-active");
                cameraView.classList.remove("lidar-active");
            } else if (mode === "LiDAR") {
                cameraTitle.innerHTML = '📡 LiDAR View - Live Feed <span class="rec">● REC</span>';
                cameraOverlay.textContent = "LiDAR POINT CLOUD • SLAM";
                cameraView.classList.add("lidar-active");
                cameraView.classList.remove("thermal-active");
            }
        });
    });
}


// ============================================================
// MANUAL / AUTOMATIC MODE
// ============================================================

function setupModeButtons() {

    const manualBtn =
        document.getElementById("manualBtn");

    const autoBtn =
        document.getElementById("autoBtn");


    if (manualBtn) {

        manualBtn.addEventListener("click", () => {

            setMode("manual");

        });

    }


    if (autoBtn) {

        autoBtn.addEventListener("click", () => {

            setMode("automatic");

        });

    }

}


function setMode(mode) {
    const manual = mode === "manual";

    const manualBtn = document.getElementById("manualBtn");
    const autoBtn = document.getElementById("autoBtn");
    const manualPanel = document.getElementById("manualPanel");
    const automaticPanel = document.getElementById("automaticPanel");
    const modeLabel = document.getElementById("modeLabel");

    if (manualBtn) manualBtn.classList.toggle("selected", manual);
    if (autoBtn) autoBtn.classList.toggle("selected", !manual);
    if (manualPanel) manualPanel.classList.toggle("hidden", !manual);
    if (automaticPanel) automaticPanel.classList.toggle("hidden", manual);
    if (modeLabel) modeLabel.textContent = manual ? "Manual" : "Automatic";

    stopAutomaticMovement();

    if (!manual && !emergencyActive) {
        startAutomaticMovement();
        updateMapModeStatus("AUTOMATIC • MOVING");
        showNotification("Rover Mode", "Automatic navigation started.");
    } else if (manual) {
        updateMapModeStatus("MANUAL • READY");
        showNotification("Rover Mode", "Manual control activated. Use the directional controls.");
    }
}


// ============================================================
// MANUAL ROVER CONTROLS
// ============================================================

function setupManualControls() {
    const actions = document.querySelectorAll(".manual-actions button");

    actions.forEach(button => {
        button.addEventListener("click", () => {
            const action = button.innerText.toLowerCase();
            if (action.includes("lights")) showNotification("Lights", "Rover lights toggled.");
            else if (action.includes("horn")) showNotification("Horn", "Rover horn activated.");
            else if (action.includes("photo")) takePhoto();
            else if (action.includes("video")) recordVideo(button);
        });
    });

    document.querySelectorAll(".joystick [data-direction]").forEach(button => {
        button.addEventListener("click", () => roverMove(button.dataset.direction));
    });

    document.addEventListener("keydown", (event) => {
        const activeManual = !document.getElementById("manualPanel")?.classList.contains("hidden");
        if (!activeManual || emergencyActive) return;
        const keys = { ArrowUp:"FORWARD", ArrowDown:"BACKWARD", ArrowLeft:"LEFT", ArrowRight:"RIGHT" };
        if (keys[event.key]) { event.preventDefault(); roverMove(keys[event.key]); }
    });
}

function roverMove(direction) {
    if (emergencyActive) return;

    // Manual mode moves the same rover marker used by Automatic mode.
    // Forward/Backward follow the mapped tunnel path; Left/Right give a
    // small visual steering adjustment.
    const step = 4;

    if (direction === "FORWARD") {
        roverState.mapIndex = Math.min(mineMapPath.length - 1, roverState.mapIndex + 1);
        roverState.y = Math.max(18, roverState.y - step);
    }
    if (direction === "BACKWARD") {
        roverState.mapIndex = Math.max(0, roverState.mapIndex - 1);
        roverState.y = Math.min(82, roverState.y + step);
    }
    if (direction === "LEFT") roverState.x = Math.max(18, roverState.x - step);
    if (direction === "RIGHT") roverState.x = Math.min(82, roverState.x + step);

    if (direction !== "STOP") {
        roverState.distance += 1;
        roverState.speed = 0.4;
    } else {
        roverState.speed = 0;
    }

    updateRoverVisual();
    updateMapRover();
    updateMapModeStatus(direction === "STOP" ? "MANUAL • STOPPED" : `MANUAL • ${direction}`);

    showNotification(
        "Rover Control",
        direction === "STOP" ? "Rover stopped." : `Rover moving ${direction}.`
    );
}

function updateRoverVisual() {
    const rover = document.getElementById("roverDot");
    if (rover) { rover.style.left = `${roverState.x}%`; rover.style.top = `${roverState.y}%`; rover.style.bottom = "auto"; }
    const distance = document.getElementById("distanceValue");
    if (distance) distance.textContent = `${roverState.distance} m`;
    const speed = document.getElementById("speedValue");
    if (speed) speed.textContent = `${roverState.speed.toFixed(1)} m/s`;
}

function updateMapRover() {
    const marker = document.getElementById("roverMapMarker");
    if (!marker) return;
    const [x,y] = mineMapPath[roverState.mapIndex] || mineMapPath[0];
    marker.setAttribute("transform", `translate(${x} ${y})`);

    const visited = document.getElementById("visitedPath");
    if (visited) {
        const points = mineMapPath.slice(0, roverState.mapIndex + 1);
        visited.setAttribute("d", points.map((p,i) => `${i ? "L" : "M"}${p[0]} ${p[1]}`).join(" "));
    }
}

function updateMapModeStatus(text) {
    const status = document.getElementById("mapRoverStatus");
    if (status) status.textContent = text;
}

function startAutomaticMovement() {
    if (autoTimer || emergencyActive) return;

    autoTimer = setInterval(() => {
        if (emergencyActive) return;

        roverState.mapIndex = (roverState.mapIndex + 1) % mineMapPath.length;
        roverState.distance += 1;
        roverState.speed = 0.4;

        updateMapRover();

        const distance = document.getElementById("distanceValue");
        if (distance) distance.textContent = `${roverState.distance} m`;
        const speed = document.getElementById("speedValue");
        if (speed) speed.textContent = `${roverState.speed.toFixed(1)} m/s`;
    }, 650);
}

function stopAutomaticMovement() {
    if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
}


function takePhoto() {

    showNotification(
        "Camera",
        "Photo capture command sent."
    );

}


function recordVideo(button) {

    const recording =
        button.dataset.recording === "true";


    if (!recording) {

        button.dataset.recording = "true";

        button.innerHTML =
            "⏹ Stop Recording";

        showNotification(
            "Video",
            "Video recording started."
        );

    }

    else {

        button.dataset.recording = "false";

        button.innerHTML =
            "🎥 Record Video";

        showNotification(
            "Video",
            "Video recording stopped."
        );

    }

}


// ============================================================
// EMERGENCY STOP
// ============================================================

function setupEmergency() {

    const emergencyButton =
        document.querySelector(".emergency");


    if (emergencyButton) {

        emergencyButton.addEventListener(
            "click",
            () => {

                emergencyStop();

            }
        );

    }

}


function createEmergencyModal() {

    let modal =
        document.getElementById(
            "emergencyModal"
        );


    if (!modal) {

        modal =
            document.createElement("div");

        modal.id =
            "emergencyModal";

        document.body.appendChild(modal);

    }


    modal.className =
        "modal hidden";


    modal.innerHTML = `

        <div>

            <h2>
                ⚠ EMERGENCY STOP
            </h2>

            <p>
                Rover emergency stop activated.
            </p>

            <button id="emergencyOk">
                OK
            </button>

        </div>

    `;


    const okButton =
        document.getElementById(
            "emergencyOk"
        );


    if (okButton) {

        okButton.addEventListener(
            "click",
            closeEmergency
        );

    }

}


function emergencyStop() {

    emergencyActive = true;
    stopAutomaticMovement();
    roverState.speed = 0;
    updateRoverVisual();

    const modal =
        document.getElementById(
            "emergencyModal"
        );


    if (!modal) return;


    modal.classList.remove("hidden");


    showNotification(
        "EMERGENCY",
        "Rover emergency stop activated."
    );

}


function closeEmergency() {

    emergencyActive = false;

    const modal =
        document.getElementById(
            "emergencyModal"
        );


    if (modal) {

        modal.classList.add(
            "hidden"
        );

    }

}


// ============================================================
// MAP INTERACTION
// ============================================================

function setupMapInteractions() {
    const zoomIn = document.getElementById("mapZoomIn");
    const zoomOut = document.getElementById("mapZoomOut");
    const reset = document.getElementById("mapReset");
    const map = document.getElementById("mineMap");

    let zoom = 1;

    function applyZoom() {
        const svg = map?.querySelector(".mine-map-svg");
        if (svg) svg.style.transform = `scale(${zoom})`;
        if (svg) svg.style.transformOrigin = "center";
    }

    zoomIn?.addEventListener("click", () => { zoom = Math.min(1.5, zoom + 0.1); applyZoom(); });
    zoomOut?.addEventListener("click", () => { zoom = Math.max(0.9, zoom - 0.1); applyZoom(); });
    reset?.addEventListener("click", () => { zoom = 1; applyZoom(); });

    document.querySelectorAll(".map-risk").forEach(marker => {
        marker.addEventListener("click", () => {
            showNotification("Mine Risk", marker.dataset.risk || "Risk detected.");
        });
    });
}


// ============================================================
// ALERT INTERACTIONS
// ============================================================

function setupAlertInteractions() {

    const viewAll =
        document.querySelector(".view");


    if (viewAll) {

        viewAll.addEventListener(
            "click",
            () => {

                const alerts =
                    document.getElementById(
                        "alertsList"
                    );


                if (alerts) {

                    alerts.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });

                }


                showNotification(
                    "Alerts",
                    "Showing all recent alerts."
                );

            }
        );

    }

}


// ============================================================
// NOTIFICATION
// ============================================================

function showNotification(
    title,
    message
) {

    let notification =
        document.getElementById(
            "systemNotification"
        );


    if (!notification) {

        notification =
            document.createElement("div");

        notification.id =
            "systemNotification";


        notification.style.position =
            "fixed";

        notification.style.right =
            "25px";

        notification.style.bottom =
            "25px";

        notification.style.zIndex =
            "10000";

        notification.style.background =
            "#18221f";

        notification.style.color =
            "#fff";

        notification.style.padding =
            "15px 18px";

        notification.style.borderRadius =
            "10px";

        notification.style.boxShadow =
            "0 8px 25px rgba(0,0,0,0.25)";

        notification.style.minWidth =
            "260px";


        document.body.appendChild(
            notification
        );

    }


    notification.innerHTML = `

        <strong>${title}</strong>

        <div
            style="
                margin-top:5px;
                font-size:13px;
                color:#ddd;
            "
        >
            ${message}
        </div>

    `;


    notification.style.display =
        "block";


    clearTimeout(
        notification.hideTimer
    );


    notification.hideTimer =
        setTimeout(
            () => {

                notification.style.display =
                    "none";

            },
            2500
        );

}


// ============================================================
// FILE SELECTION
// ============================================================

function fileFromInput() {

    const input =
        document.createElement("input");

    input.type = "file";

    input.accept = "image/*";


    return new Promise(resolve => {

        input.onchange = () => {

            if (
                input.files &&
                input.files.length > 0
            ) {

                resolve(
                    input.files[0]
                );

            }

            else {

                resolve(null);

            }

        };


        input.click();

    });

}


// ============================================================
// AI ANALYSIS
// ============================================================

async function analyze() {

    const image =
        await fileFromInput();


    if (!image) {

        showNotification(
            "AI Analysis",
            "No image selected."
        );

        return;

    }


    const fd =
        new FormData();


    fd.append(
        "image",
        image
    );


    const sensorIds = [

        "CH4",
        "CO",
        "CO2",
        "O2",
        "temperature",
        "humidity"

    ];


    sensorIds.forEach(id => {

        const element =
            document.getElementById(id);


        if (element) {

            fd.append(
                id,
                element.value
            );

        }

    });


    const list =
        document.getElementById(
            "alertsList"
        );


    if (list) {

        list.innerHTML = `

            <div class="alert">

                ⏳ <b>
                    AI analysis running...
                </b>

                <small>
                    Sending image and sensor data to FastAPI.
                </small>

            </div>

        `;

    }


    showNotification(
        "AI Analysis",
        "Sending image to backend..."
    );


    try {

        const res =
            await fetch(
                API_URL,
                {
                    method: "POST",
                    body: fd
                }
            );


        if (!res.ok) {

            throw new Error(
                "API returned HTTP " +
                res.status
            );

        }


        const data =
            await res.json();


        updateDashboard(data);


        showNotification(
            "AI Analysis Complete",
            "Analysis results received successfully."
        );


    }

    catch (err) {

        console.error(err);


        if (list) {

            list.innerHTML = `

                <div class="alert critical">

                    ❌ <b>
                        Backend connection failed
                    </b>

                    <small>
                        ${err.message}.
                        Make sure FastAPI is running on port 8000.
                    </small>

                </div>

            `;

        }


        showNotification(
            "Backend Error",
            "Could not connect to FastAPI."
        );

    }

}


// ============================================================
// UPDATE DASHBOARD AFTER AI ANALYSIS
// ============================================================

function updateDashboard(d) {

    const overall =
        String(
            d.overall_risk ??
            "UNKNOWN"
        ).toUpperCase();


    const worker =
        String(
            d.worker ??
            "UNKNOWN"
        ).toUpperCase();


    const helmet =
        String(
            d.helmet ??
            "UNKNOWN"
        ).toUpperCase();


    const fire =
        String(
            d.fire ??
            "UNKNOWN"
        ).toUpperCase();


    const smoke =
        String(
            d.smoke ??
            "UNKNOWN"
        ).toUpperCase();


    const status =
        document.querySelector(
            ".status"
        );


    if (status) {

        status.textContent =
            overall === "CRITICAL"
                ? "Critical"
                : "Normal";


        status.style.background =
            overall === "CRITICAL"
                ? "#e33"
                : "#20a75a";

    }


    const list =
        document.getElementById(
            "alertsList"
        );


    if (!list) return;


    list.innerHTML = `

        <div class="alert
            ${overall === "CRITICAL"
                ? "critical"
                : ""}">

            ${overall === "CRITICAL"
                ? "🚨"
                : "ℹ️"}

            <b>
                Overall Risk: ${overall}
            </b>

            <small>

                Vision Risk:
                ${d.vision_risk ?? "N/A"}

                |

                Gas Risk:
                ${d.gas_risk ?? "N/A"}

            </small>

        </div>


        <div class="alert">

            👷
            <b>
                Worker: ${worker}
            </b>

            <small>
                Helmet: ${helmet}
            </small>

        </div>


        <div class="alert">

            🔥
            <b>
                Fire: ${fire}
            </b>

            <small>
                Smoke: ${smoke}
            </small>

        </div>

    `;

}


// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================

document.addEventListener(
    "keydown",
    event => {

        if (event.key === "Escape") {

            closeEmergency();

        }


        if (
            event.key.toLowerCase() === "m"
        ) {

            setMode("manual");

        }


        if (
            event.key.toLowerCase() === "a"
        ) {

            setMode("automatic");

        }

    }
);