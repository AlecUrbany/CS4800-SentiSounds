      const email = localStorage.getItem("email")
      let exportMap = {};
      let allSongsData = {};
      let isAuthenticated = false;
      let pastPrompt = ""
      let popularityControl = 0;
      let currentPlayingAudio = null;
      if (!email){
        document.getElementById("connectSpotifyBtn").style.visibility = "hidden";
        document.getElementById("spotifyImg").style.visibility = "hidden";
        document.getElementById("signOutBtn").style.display = "none";
        document.getElementById("signUpBtn").style.display = "block";
      } else {
        document.getElementById("signUpBtn").style.display = "none";
        document.getElementById("signOutBtn").style.display = "block";

        const formData = new FormData();
        formData.append("email_address", email);
        fetch(`${baseURL}/spotify-check-authentication`, {
          method: "POST",
          body: formData,
        })
        .then((response) => response.json())
                  .then((data) => {
                    isAuthenticated = data.is_authenticated;
                    if (isAuthenticated) {
                      document.getElementById("connectSpotifyBtn").style.visibility = "hidden";
                      document.getElementById("spotifyImg").style.visibility = "hidden";
                    } else { // Not authenticated
                      document.getElementById("exportPlaylistBtn").style.visibility = "hidden";
                      document.getElementById("playlistContainer").style.visibility = "hidden";
                      document.getElementById('addAllToPlaylistBtn').style.visibility = "hidden";
                      document.getElementById('removeAllFromPlaylistBtn').style.visibility = "hidden";
                      document.getElementById("connectSpotifyBtn").style.visibility = "visible";
                      document.getElementById("spotifyImg").style.visibility = "visible";
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
          disabledButtons(true);
          rickroll();
          const enteredPrompt = document.getElementById("default-search").value;
          const loader = document.getElementById("loader");
          const songsContainer = document.getElementById("songsContainer");
          const popularityScore = getPopularityScore(enteredPrompt);
          pastPrompt = enteredPrompt;

          loader.style.display = "block";
          songsContainer.style.display = "none";

          const formData = new FormData();
          formData.append('email_address', email);

          const params = new URLSearchParams({
            entered_prompt: enteredPrompt,
            popularity_score: popularityScore,
          });

          const url = `${baseURL}/recommend-songs?${params.toString()}`;
          fetch(url, {
            method: "POST",
            body: formData,
          })
            .then((response) => response.json())
            .then((data) => {
              setTimeout(() => {
                if (data.status === "success") {
                  disabledButtons(false);
                  songsContainer.innerHTML = "";
                  document.querySelector(".playlist-toggler").style.visibility = isAuthenticated ? "visible" : "hidden";
                  document.getElementById("exportPlaylistBtn").style.visibility = isAuthenticated ? "visible" : "hidden";
                  document.getElementById("playlistContainer").style.visibility = isAuthenticated ? "visible" : "hidden";
                  document.getElementById('addAllToPlaylistBtn').style.visibility = isAuthenticated ? "visible" : "hidden";
                  document.getElementById('removeAllFromPlaylistBtn').style.visibility = isAuthenticated ? "visible" : "hidden";

                  data.songs.forEach((song) => {
                    // Store song details in object map
                    allSongsData[song.id] = {
                      artistName: song.artists
                        .map((artist) => artist.name)
                        .join(", "),
                      songId: song.id,
                      songName: song.name,
                      previewUrl: song.preview_url,
                      likedByUser: song.liked_by_user,
                      youtubeUrl:
                        song.external_urls.youtube ||
                        "No YouTube URL available",
                    };
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
                            <button onclick="togglePlayPause('audio-${song.id}')"><i class="fas ${song.isPlaying ? 'fa-pause' : 'fa-play'}" id="icon-${song.id}"></i></button>
                            <input type="range" id="progress-${song.id}" value="0" max="100" class="progress-bar" oninput="setAudioPosition(this, 'audio-${song.id}')">
                            <span id="time-${song.id}">0:00/0:00</span>
                            <input type="range" id="volume-${song.id}" value="100" min="0" max="100" class="volume-slider" oninput="setVolume(this, 'audio-${song.id}')">
                            <i class="fas fa-volume-up" style="margin-right: 5px;"></i>
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
                                    <div class="flex justify-between items-center" style="display:flex">
                                      <button class="like-button text-black-500 focus:outline-none focus:text-black-700" data-song-id="${song.id}">
                                        ${song.liked_by_user ? '<i class="fas fa-heart liked"></i>' : '<i class="fas fa-heart"></i>'}
                                      </button>
                                      <div style="margin-left:15px">
                                        <button class="augment-button text-black-500 focus:outline-none focus:text-black-700" data-song-id="${song.id}">
                                          ${Object.hasOwn(exportMap, song.id) ? '<i class="fas fa-plus augmented"></i>' : '<i class="fas fa-plus"></i>'}
                                        </button>
                                      </div>
                                    </div>
                                </div>`;
                    songsContainer.appendChild(songElement);

                    if (song.liked_by_user) {
                      songElement.querySelector(".like-button").classList.add("liked");
                    }
                    if (Object.hasOwn(exportMap, song.id)) {
                      songElement.querySelector(".augment-button").classList.add("augmented");
                    }
                  });
                  loader.style.display = "none";
                  songsContainer.style.display = "grid";
                  [].forEach.call(document.querySelectorAll(".like-button"), function (button) {
                    button.style.visibility = isAuthenticated ? "visible" : "hidden";
                  });
                  [].forEach.call(document.querySelectorAll(".augment-button"), function (button) {
                    button.style.visibility = isAuthenticated ? "visible" : "hidden";
                  });
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

                    document
                    .querySelectorAll(".augment-button")
                    .forEach((button) => {
                      button.addEventListener("click", function () {
                        const songId = this.getAttribute("data-song-id");
                        if (this.classList.contains("augmented")) {
                          deaugmentPlaylist(this, songId);
                        } else {
                          augmentPlaylist(this, songId);
                        }
                      });
                    });

                    document.getElementById('addAllToPlaylistBtn').addEventListener('click', function() {
                      document.querySelectorAll(".augment-button").forEach((button) => {
                          const songId = button.getAttribute("data-song-id"); // Get song ID from button
                          if (!Object.hasOwn(exportMap, songId)) { // Check if the song is not already added
                              augmentPlaylist(button, songId); // Use the correct song ID for each button
                          }
                      });
                    });
                    document.getElementById('removeAllFromPlaylistBtn').addEventListener('click', function() {
                      document.querySelectorAll(".augment-button").forEach((button) => {
                          const songId = button.getAttribute("data-song-id"); // Get song ID from button
                          if (Object.hasOwn(exportMap, songId)) { // Check if the song is not already added
                              deaugmentPlaylist(button, songId); // Use the correct song ID for each button
                          }
                      });
                      const removeSongs = Object.keys(exportMap);
                      removeSongs.forEach(songIds => {
                        deaugmentManualPlaylist(songIds);
                      });
                    });
                } else {
                  console.error("Failed to get recommended songs:", data.error);
                  document.getElementById("exportPlaylistBtn").style.visibility = "hidden";  //Should hopefully hide export playlist button when songs have not been listed.
                  document.getElementById("playlistContainer").style.visibility = "hidden";
                  document.getElementById('addAllToPlaylistBtn').style.visibility = "hidden";
                  document.getElementById('removeAllFromPlaylistBtn').style.visibility = "hidden";
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

      function setVolume(slider, audioId) {
        const audio = document.getElementById(audioId);
        audio.volume = slider.value / 100;
      }

      function togglePlayPause(audioId) {
        const audio = document.getElementById(audioId);
        const icon = document.getElementById('icon-' + audioId.split('-')[1]);

        // Check if there's a currently playing audio, and it's not the one being toggled
        if (currentPlayingAudio && currentPlayingAudio !== audio && !currentPlayingAudio.paused) {
            currentPlayingAudio.pause();
            const currentIcon = currentPlayingAudio.parentElement.querySelector('.fa-pause');
            if (currentIcon) {
                currentIcon.classList.replace('fa-pause', 'fa-play');
            }
            currentPlayingAudio = null;
        }

        // Toggle play/pause on the current audio
        if (audio.paused) {
            currentPlayingAudio = audio;
            audio.play();
            icon.classList.remove('fa-play');
            icon.classList.add('fa-pause');
        } else {
            audio.pause();
            icon.classList.remove('fa-pause');
            icon.classList.add('fa-play');
        }
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

      function augmentPlaylist(that, songId) {
        exportMap[songId] = allSongsData[songId];
        const playlistElement = document.createElement("div");
        playlistElement.classList.add("playlist-song");
        playlistElement.setAttribute("data-song", songId);
        playlistElement.innerHTML =
        `<div class="playlist-item flex justify-between items-center">
            <div class="song-details">
                <h3 class="text-sm font-bold">${allSongsData[songId].songName} - ${allSongsData[songId].artistName}</h3>
            </div>
            <div class="button-container">
                <button class="deaugment-button text-black-500 focus:outline-none focus:text-black-700" data-song-id="${songId}">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        </div>`;
        that.classList.add("augmented");
        that.innerHTML = '<i class="fas fa-plus augmented"></i>'; // Change to filled heart
        document.getElementById("playlistContainer").appendChild(playlistElement);
        playlistElement.querySelector(".deaugment-button").addEventListener("click", function () {
          deaugmentPlaylist(that, songId);
        });
      }

      function deaugmentPlaylist(that, songId) {
        delete exportMap[songId];
        // const songsContainer = document.getElementById("songsContainer");
        that.classList.remove("augmented");
        that.innerHTML = '<i class="fas fa-plus"></i>'; // Change to unfilled heart
        const playlistContainer = document.getElementById("playlistContainer");
        const playlistElement = playlistContainer.querySelector(`[data-song="${songId}"]`);
        console.log(playlistElement);
        playlistContainer.removeChild(playlistElement);
      }

      function deaugmentManualPlaylist(songId) {
        delete exportMap[songId];
        // that.classList.remove("augmented");
        // that.innerHTML = '<i class="fas fa-plus"></i>'; // Change to unfilled heart
        const playlistContainer = document.getElementById("playlistContainer");
        const playlistElement = playlistContainer.querySelector(`[data-song="${songId}"]`);
        playlistContainer.removeChild(playlistElement);
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
        fetch(`${baseURL}${endpoint}?song_id=${songId}`, {
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

      function getPopularityScore(enteredPrompt) {
        if (enteredPrompt === pastPrompt) {
          popularityControl = popularityControl + 5;
          if (popularityControl >= 20) {
            return 5;
          } else {
            return 20 - popularityControl;
          }
        } else {
          popularityControl = 0;
          return 20;
        }
      }

      function rickroll() {
        const randomNumber = Math.random();
        const rarityThreshold = 0.01;

        if (randomNumber < rarityThreshold) {
            window.open("https://youtu.be/dQw4w9WgXcQ?si=rhMz56ysUWlu-0OH", "You Won!");
        } else {
            console.log(":)")
        }
      }

      function disabledButtons(boolean) {
        document.getElementById("searchButton").disabled = boolean;
        document.getElementById("exportPlaylistBtn").disabled = boolean;
        document.getElementById("playlistContainer").disabled = boolean;
        document.getElementById('addAllToPlaylistBtn').disabled = boolean;
        document.getElementById('removeAllFromPlaylistBtn').disabled = boolean;
      }

      document.getElementById("signOutBtn").addEventListener("click", function() {
        // Clear authentication data
        localStorage.removeItem('email');

        location.replace('index.html');
      });

      const playlistToggler = document.querySelector(".playlist-toggler");
      const closePlaylistBtn = document.querySelector(".close-btn");

      playlistToggler.style.visibility = isAuthenticated ? "visible" : "hidden";

      closePlaylistBtn.addEventListener("click", () => document.body.classList.remove("show-songs-management"));
      playlistToggler.addEventListener("click", () => document.body.classList.toggle("show-songs-management"));

      function getSongIdsAsString() {
        // Retrieve all keys (song IDs) from the exportMap
        const allSongIds = Object.keys(exportMap);

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
      //console.log("Code extracted from URL:", code);

      if (code.length > 5) {
        document.addEventListener("DOMContentLoaded", async function () {

          // Retrieving data from localStorage
          const email = localStorage.getItem('email');
          const formData = new FormData();
          formData.append("email_address", email);
          formData.append("code", code);

          try {
            const response = await fetch(`${baseURL}/spotify-authenticate`, {
              method: "POST",
              body: formData,
            });

            const data = await response.json();

            if (response.ok) {
              alert("Spotify Authentication successful.");
              window.location.href = "index.html";
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
          fetch(`${baseURL}/spotify-auth-link`)
            .then((response) => response.json())
            .then((data) => {
              if (data.status === "success") {
                window.open(data.url, "_self"); // Opens the Spotify URL in a new tab
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

          if (songIdsString.length < 5){
            alert("No songs have been added to the playlist!");
            return;
          }

          const params = new URLSearchParams({
            song_ids: songIdsString,
            playlist_description: document.getElementById("default-search").value
          });
          const url = `${baseURL}/export-playlist?${params.toString()}`;
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
              window.open(data.playlist_url)
            } else {
              alert(data.error);
            }
          } catch (error) {
            // console.error('Error during authentication:', error);
            alert("An error occurred during exporting. Please try again.");
          }
        });
      });
