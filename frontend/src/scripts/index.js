      const email = localStorage.getItem("email")
      const api_uri = "http://10.0.0.5:5000/";
      song_id_list = "";
      let songDetailsMap = {};
      let allSongsData = {};

      if (!email){
        document.getElementById("connectSpotifyBtn").hidden = true;
        document.getElementById("spotifyImg").hidden = true;
        document.getElementById("exportPlaylistBtn").hidden = true;
      } else {
        document.getElementById("signUpBtn").hidden = true;

        const formData = new FormData();
        formData.append("email_address", email);
        fetch(`${api_uri}/spotify-check-authentication`, {
          method: "POST",
          body: formData,
        })
        .then((response) => response.json())
                  .then((data) => {
                    if (data.is_authenticated == true) {
                      document.getElementById("exportPlaylistBtn").hidden = false;
                    } else {
                      document.getElementById("exportPlaylistBtn").hidden = true;
                      document.getElementById("connectSpotifyBtn").hidden = false;
                      document.getElementById("spotifyImg").hidden = false;
                    }
                  })
                  .catch((error) => {
                    console.error(`Error checking Spotify auth:`, error);
                  });

      }

      document
        .getElementById("searchForm")
        .addEventListener("submit", function (event) {
          event.preventDefault();
          const enteredPrompt = document.getElementById("default-search").value;
          const loader = document.getElementById("loader");
          const songsContainer = document.getElementById("songsContainer");
          const popularityScore =
            document.getElementById("number-select").value;

          loader.style.display = "block";
          songsContainer.style.display = "none";

          const formData = new FormData();
          formData.append('email_address', email);

          const params = new URLSearchParams({
            entered_prompt: enteredPrompt,
            popularity_score: popularityScore,
          });

          const url = `${api_uri}/recommend-songs?${params.toString()}`;
          fetch(url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            contentType: "application/json",
            body: formData,
          })
            .then((response) => response.json())
            .then((data) => {
              setTimeout(() => {
                if (data.status === "success") {
                  songsContainer.innerHTML = "";
                  data.songs.forEach((song) => {
                    // Store song details in hashmap
                    allSongsData[song.id] = {
                      artistName: song.artists
                        .map((artist) => artist.name)
                        .join(", "),
                      songId: song.id,
                      songName: song.name,
                      previewUrl: song.preview_url,
                      youtubeUrl:
                        song.external_urls.youtube ||
                        "No YouTube URL available",
                    };
                    console.log(songDetailsMap[song.id]);
                    const songElement = document.createElement("div");
                    songElement.classList.add(
                      "genre-card",
                      "custom-orange-bg",
                      "p-4",
                      "rounded"
                    );
                    const albumCoverUrl =
                      song.album.images.length > 0
                        ? song.album.images[0].url
                        : "https://placehold.co/200x200";
                    const artistNames = song.artists
                      .map((artist) => artist.name)
                      .join(", ");

                    let audioControls = "";
                    if (song.preview_url) {
                      audioControls = `
                                    <audio id="audio-${song.id}" src="${song.preview_url}" ontimeupdate="updateProgress(this)" onloadedmetadata="updateProgress(this)"></audio>
                                    <div class="audio-controls">
                                        <button onclick="document.getElementById('audio-${song.id}').play()"><i class="fas fa-play"></i></button>
                                        <button onclick="document.getElementById('audio-${song.id}').pause()"><i class="fas fa-pause"></i></button>
                                        <input type="range" id="progress-${song.id}" value="0" max="100" class="progress-bar" oninput="setAudioPosition(this, 'audio-${song.id}')">
                                        <span id="time-${song.id}">0:00/0:00</span>
                                    </div>
                                `;
                    }

                    let youtubeButtonHTML = "";
                    if (song.external_urls.youtube) {
                      youtubeButtonHTML = `<a href="${song.external_urls.youtube}" target="_blank" class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded">YouTube</a>`;
                    }

                    songElement.innerHTML = `
                                <div class="flex justify-between items-center">
                                    <div>
                                        ${youtubeButtonHTML}
                                        <img src="${albumCoverUrl}" alt="${song.name} album cover" class="rounded mb-2" style="width:200px; height:200px;">
                                        <h3 class="text-xl font-bold">${song.name} - ${artistNames}</h3>
                                        ${audioControls}
                                    </div>
                                    <button class="like-button text-black-500 focus:outline-none focus:text-black-700" data-song-id="${song.id}">
                                        <i class="fas fa-heart"></i>
                                    </button>
                                </div>`;
                    songsContainer.appendChild(songElement);
                  });
                  loader.style.display = "none";
                  songsContainer.style.display = "grid";

                  document
                    .querySelectorAll(".like-button")
                    .forEach((button) => {
                      button.addEventListener("click", function () {
                        const songId = this.getAttribute("data-song-id");
                        if (this.classList.contains("liked")) {
                          handleSongInteraction(songId, email, "unlike");
                          this.classList.remove("liked");
                          this.innerHTML = '<i class="fas fa-heart"></i>'; // Change to unfilled heart
                        } else {
                          handleSongInteraction(songId, email, "like");
                          this.classList.add("liked");
                          this.innerHTML = '<i class="fas fa-heart liked"></i>'; // Change to filled heart
                        }
                      });
                    });
                } else {
                  console.error("Failed to get recommended songs:", data.error);
                }
              }, 3000);
            })
            .catch((error) => {
              console.error("Error fetching data:", error);
            });
        });

      function updateProgress(audio) {
        const progressBar = document.getElementById(
          "progress-" + audio.id.split("-")[1]
        );
        const percentage = Math.floor(
          (100 / audio.duration) * audio.currentTime
        );
        progressBar.value = percentage;
        const currentTimeDisplay = formatTime(audio.currentTime);
        const durationDisplay = formatTime(audio.duration);
        const timeLabel = document.getElementById(
          "time-" + audio.id.split("-")[1]
        );
        timeLabel.textContent = `${currentTimeDisplay}/${durationDisplay}`;
      }

      function setAudioPosition(progressBar, audioId) {
        const audio = document.getElementById(audioId);
        const duration = audio.duration;
        audio.currentTime = (progressBar.value / 100) * duration;
      }

      function formatTime(timeInSeconds) {
        const minutes = Math.floor(timeInSeconds / 60);
        const seconds = Math.floor(timeInSeconds % 60);
        return `${minutes}:${seconds < 10 ? "0" + seconds : seconds}`;
      }

      function handleSongInteraction(songId, email, action) {
        if (!email) {
          console.error("User email is required.");
          return; // Stop the function if email is not provided
        }
        const endpoint =
          action === "like" ? "/spotify-like-song" : "/spotify-unlike-song";
        const formData = new FormData();
        formData.append("email_address", email);
        if (action === "like") {
          songDetailsMap[songId] = allSongsData[songId];
        } else if (action === "unlike") {
          delete songDetailsMap[songId];
        }
        console.log(songDetailsMap);
        // song_id_list = song_id_list.concat(songId, " ");
        // console.log(song_id_list);
        fetch(`${api_uri}${endpoint}?song_id=${songId}`, {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              console.log(`Song ${action}d successfully.`);
            } else {
              console.error(`Failed to ${action} song:`, data.error);
            }
          })
          .catch((error) => {
            console.error(`Error ${action}ing song:`, error);
          });
      }

      function getSongIdsAsString() {
        // Retrieve all keys (song IDs) from the songDetailsMap
        const allSongIds = Object.keys(songDetailsMap);

        // Join all song IDs into a string separated by spaces
        const songIdsString = allSongIds.join(" ");

        return songIdsString;
      }

      function getURLParameter(name) {
        const regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
        const results = regex.exec(window.location.search);
        return results === null
          ? ""
          : decodeURIComponent(results[1].replace(/\+/g, " "));
      }

      // Extract the 'code' parameter from the URL
      const code = getURLParameter("code");

      // You can now use 'code' variable throughout your script
      console.log("Code extracted from URL:", code);

      if (code.length > 5) {
        document.addEventListener("DOMContentLoaded", async function () {

          // Retrieving data from localStorage
          const email = localStorage.getItem('email');
          const formData = new FormData();
          formData.append("email_address", email);
          formData.append("code", code);

          try {
            const response = await fetch(`${api_uri}/spotify-authenticate`, {
              method: "POST",
              body: formData,
            });

            const data = await response.json();

            if (response.ok) {
              alert("Spotify Authentication successful.");
              // window.location.href = "index.html";
            } else {
              alert(data.error);
            }
          } catch (error) {
            console.error("Error during Spotify authentication:", error);
            alert(
              "An error occurred during Spotify Authentication. Please try again."
            );
          }
        });
      }

      document
        .getElementById("connectSpotifyBtn")
        .addEventListener("click", function () {
          fetch(`${api_uri}/spotify-auth-link`)
            .then((response) => response.json())
            .then((data) => {
              if (data.status === "success") {
                window.open(data.url, "_blank"); // Opens the Spotify URL in a new tab
              } else {
                console.error("Failed to connect to Spotify:", data.error);
              }
            })
            .catch((error) => {
              console.error("Error fetching the Spotify link:", error);
            });
        });

      document
        .getElementById("signUpBtn")
        .addEventListener("click", function () {
          window.location.href = "signup.html"
        });

      document.addEventListener("DOMContentLoaded", function () {
        const exportButton = document.querySelector("#exportPlaylistBtn");
        exportButton.addEventListener("click", async function () {
          // Example usage:
          const songIdsString = getSongIdsAsString();
          console.log(songIdsString); // Output will be something like "id1 id2 id3"
          const params = new URLSearchParams({
            song_ids: songIdsString,
            playlist_name: "SentiSounds Export",
            playlist_description: "",
          });
          const url = `${api_uri}/export-playlist?${params.toString()}`;
          // Retrieving data from localStorage
          const email = localStorage.getItem('email');

          const formData = new FormData();
          formData.append("email_address", email);

          try {
            const response = await fetch(url, {
              method: "POST",
              body: formData,
            });

            const data = await response.json();

            if (response.ok) {
              alert("Spotify Playlist Export successful.");
              // window.location.href = "index.html";
            } else {
              alert(data.error);
            }
          } catch (error) {
            // console.error('Error during authentication:', error);
            alert("An error occurred during exporting. Please try again.");
          }
        });
      });
