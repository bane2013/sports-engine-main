document
	.querySelector("form")
	.addEventListener("submit", async function (event) {
		event.preventDefault()

		// Get the selected radio button
		const selectedRadio = document.querySelector(
			'input[name="btnradio"]:checked'
		).nextElementSibling.textContent

		// Get the input text value
		const query = document.getElementById("searchBox").value

		// Print the results to the console
		console.log(`Selected Option: ${selectedRadio}`)
		console.log(`Query: ${query}`)

		if (!query) {
			alert("Please enter a search term")
			return
		}

		try {
			const response = await fetch(
				`http://127.0.0.1:5000/search?q=${encodeURIComponent(query)}`
			)
			if (!response.ok) {
				throw new Error("Network response was not ok")
			}

			const results = await response.json()
			const resultsDiv = document.getElementById("results")
			resultsDiv.innerHTML = "" // Clear previous results

			if (results.length === 0) {
				resultsDiv.innerHTML = "<p>No results found</p>"
			} else {
				results.forEach((result) => {
					const div = document.createElement("div")
					div.classList.add("queryResultItem")
					div.innerHTML = `
                    <h4><a href="${result[1]}" target="_blank">${result[0]}</a></h4> <!-- Title -->
                    <p>${result[2]}</p> <!-- Description -->
                `
					resultsDiv.appendChild(div)
				})
			}
		} catch (error) {
			console.error("Error during search:", error)
			alert(
				"An error occurred while fetching search results. Please check your backend server."
			)
		}
	})
