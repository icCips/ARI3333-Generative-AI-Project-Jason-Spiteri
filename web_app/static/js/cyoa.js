document.addEventListener("DOMContentLoaded", () => {

    const configureSection = document.querySelector(".configure-section");
    const form = configureSection.querySelector("form");
    const lockInButton = document.getElementById("lock-in");
    const storyBox = document.querySelector(".story-box p");
    const goButton = document.getElementById("reply");
    const userSubmissionInput = document.getElementById("user-submission");
    const saveButton = document.getElementById("save");
    const loadButton = document.getElementById("load");
    const clearButton = document.getElementById("clear");

    // Toggle visibility of the form on Configure section click
    configureSection.addEventListener("click", (event) => {
        // Check if the click is on the section and not on the form or button
        if (!form.contains(event.target) && event.target !== lockInButton) {
            configureSection.classList.toggle("active"); // Toggle active class
        }
    });

    // Handle Lock In button click
    lockInButton.addEventListener("click", (event) => {
        event.preventDefault();

        // Gather all form data
        const characterName = document.getElementById("character-name").value;
        const bkCharacterNames = document.getElementById("bk-character-names").value;
        const timePeriod = document.getElementById("time").value;
        const location = document.getElementById("location").value;
        const lore = document.getElementById("lore").value;
        const gritty = document.getElementById("gritty").checked;
        const realistic = document.getElementById("realistic").checked;
        const challenge = document.getElementById("challenge").checked;

        // Send form data via fetch
        fetch("/cyoa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: "configure",
                "character-name": characterName,
                "bk-character-names": bkCharacterNames,
                time: timePeriod,
                location: location,
                lore: lore,
                gritty: gritty ? "true" : "false",
                realistic: realistic ? "true" : "false",
                challenge: challenge ? "true" : "false",
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Configuration response:", data);
                storyBox.innerHTML = `<p>${data.story}</p>`;
            })
            .catch((error) => {
                console.error("Error configuring story:", error);
            });

        configureSection.classList.remove("active");
    });

    // Handle Go button click
    goButton.addEventListener("click", (event) => {
        event.preventDefault();

        console.log(storyBox.innerHTML)

        const userSubmission = userSubmissionInput.value;
        userSubmissionInput.value = ""; // Clear the input field
        storyBox.innerHTML += `<hr><p>${userSubmission}</p><hr>`;

        fetch("/cyoa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: "submit",
                "user-submission": userSubmission,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Story continuation response:", data);
                storyBox.innerHTML += `<p>${data.story}</p>`;
            })
            .catch((error) => {
                console.error("Error submitting user input:", error);
            });
    });

    // Handle Clear button click
    clearButton.addEventListener("click", (event) => {
        event.preventDefault();

        fetch("/cyoa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name: "clear" }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Clear response:", data);
                storyBox.innerHTML = "Once upon a time..."; // Clear the story box content
            })
            .catch((error) => {
                console.error("Error clearing story:", error);
            });
    });

    // Save and load button handlers remain unchanged
    saveButton.addEventListener("click", (event) => {
        event.preventDefault(); // Prevent default form submission behavior
    
        // Send the story and conversation data to the server via the `/cyoa` route
        fetch("/cyoa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: "save",
                story: storyBox.innerHTML, // Send story content
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Story saved successfully:", data);
    
                const blob = new Blob([data.savedFile], { type: "text/html" });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);

                const timePeriod = document.getElementById("time").value;
                const location = document.getElementById("location").value;

                link.download = location + " " + timePeriod + ".html";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            })
            .catch((error) => {
                console.error("Error saving story:", error);
            });
    });    
    
    loadButton.addEventListener("click", (event) => {
        event.preventDefault();
    
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.accept = ".html";
    
        fileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
    
                reader.onload = (e) => {
                    const fileContent = e.target.result;
    
                    // Send the file content to the server via the `/cyoa` route
                    fetch("/cyoa", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            name: "load",
                            loadedFile: fileContent, // Send the loaded file content
                        }),
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! Status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then((data) => {
                            console.log("Story loaded successfully:", data);
    
                            storyBox.innerHTML = data.story;
    
                            // Clear and update the conversation on the server
                            console.log("Conversation restored:", data.conversation);
                        })
                        .catch((error) => {
                            console.error("Error loading story:", error);
                        });
                };
    
                reader.onerror = () => {
                    alert("Failed to read the file. Please try again.");
                };
    
                reader.readAsText(file);
            }
        });
    
        fileInput.click();
    });
    
});
