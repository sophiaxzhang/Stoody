import axios from 'axios'; // Import Axios with ES module syntax

// Hardcode your Canvas Access Token and Canvas Instance URL
const accessToken = '10~8NfMxaeLV6XHz3a3f6XVByLK8yXnnut7KJWxFyT2X4tUkKV9A94AweMYfZ4FkatE';
const canvasInstance = 'canvas.uw.edu'; // Replace with your actual Canvas instance URL

// Function to get course information from Canvas
async function getCourses() {
  try {
    // Make GET request using Axios
    const response = await axios.get(`https://${canvasInstance}/api/v1/courses`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    // Log the course data
    console.log(response.data);
  } catch (error) {
    console.error('Error fetching courses:', error.message);
  }
}

// Call the function to fetch the courses
getCourses();
