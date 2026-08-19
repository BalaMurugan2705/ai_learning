async function uploadDocument() {

    const fileInput =
        document.getElementById("fileInput");

    const status =
        document.getElementById("uploadStatus");


    if (!fileInput.files.length) {

        status.textContent =
            "Please choose a file.";

        return;
    }


    const file =
        fileInput.files[0];


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    status.textContent =
        "Uploading...";


    const response =
        await fetch(
            "/upload",
            {
                method: "POST",
                body: formData
            }
        );


    const data =
        await response.json();


    if (!response.ok) {

        status.textContent =
            "Upload failed.";

        return;
    }


   status.textContent =
    `${data.message} ` +
    `${data.filename}: ` +
    `${data.chunks_indexed} chunks created.`;
}

async function askQuestion() {
const askButton =
    document.getElementById("askButton");

askButton.disabled = true;

askButton.textContent =
    "Thinking...";
    const questionInput =
        document.getElementById("question");

    const versionInput =
        document.getElementById("sdkVersion");


    const question =
        questionInput.value.trim();


    const sdkVersion =
        versionInput.value;


    if (!question) {

        document.getElementById("answer")
            .textContent =
            "Please enter a question.";

        return;
    }


    document.getElementById("answer")
        .textContent =
        "Thinking...";


    document.getElementById("sources")
        .textContent =
        "";


    const response =
        await fetch(
            "/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    question: question,

                    sdk_version:
                        sdkVersion || null

                })
            }
        );


   if (data.error) {

    status.textContent =
        data.error;

    return;
}


    if (!response.ok) {

        document.getElementById("answer")
            .textContent =
            "Something went wrong.";

        return;
    }


    document.getElementById("answer")
        .textContent =
        data.answer;


    displaySources(
        data.sources
    );
}

function displaySources(sources) {

    const sourcesContainer =
        document.getElementById("sources");


    if (!sources || sources.length === 0) {

        sourcesContainer.textContent =
            "No supporting source found.";

        return;
    }


    sourcesContainer.innerHTML = "";


    sources.forEach(
        (source, index) => {

            const sourceElement =
                document.createElement("div");


            sourceElement.innerHTML = `
                <p>
                    <strong>[${index + 1}]
                    ${source.source_file}</strong>
                </p>

                <p>
                    Page: ${source.page_id}
                </p>

                <p>
                    Section: ${source.section}
                </p>

                <hr>
            `;


            sourcesContainer.appendChild(
                sourceElement
            );
        }
    );
}