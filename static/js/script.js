document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const stepCountEl = document.getElementById('stepCount');
    const cadenceEl = document.getElementById('cadence');
    const symLEl = document.getElementById('symL');
    const symREl = document.getElementById('symR');
    const symBar = document.getElementById('symBar');
    const angleLEl = document.getElementById('angleL');
    const angleREl = document.getElementById('angleR');
    const elbowLEl = document.getElementById('elbowL');
    const elbowREl = document.getElementById('elbowR');
    
    const videoUpload = document.getElementById('videoUpload');
    const imageUpload = document.getElementById('imageUpload');
    const videoFileName = document.getElementById('videoFileName');
    const imageFileName = document.getElementById('imageFileName');
    
    const youtubeUrl = document.getElementById('youtubeUrl');
    const youtubeBtn = document.getElementById('youtubeBtn');
    
    const resetBtn = document.getElementById('resetBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resumeBtn = document.getElementById('resumeBtn');
    const replayBtn = document.getElementById('replayBtn');

    const camBtn = document.getElementById('camBtn');
    const accuracySelect = document.getElementById('accuracySelect');
    
    // Tab Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Interval for fetching metrics
    let metricsInterval;

    function startMetricsPolling() {
        metricsInterval = setInterval(fetchMetrics, 500); // 2Hz update rate
    }

    async function fetchMetrics() {
        try {
            const response = await fetch('/metrics');
            const data = await response.json();
            
            updateDashboard(data);
        } catch (error) {
            console.error('Error fetching metrics:', error);
        }
    }

    function updateDashboard(data) {
        stepCountEl.innerText = data.step_count;
        cadenceEl.innerText = data.cadence;
        
        symLEl.innerText = `${data.symmetry_l}%`;
        symREl.innerText = `${data.symmetry_r}%`;
        symBar.style.width = `${data.symmetry_l}%`; 

        angleLEl.innerText = data.l_knee_angle ? `${Math.round(data.l_knee_angle)}°` : '--°';
        angleREl.innerText = data.r_knee_angle ? `${Math.round(data.r_knee_angle)}°` : '--°';
        
        // Elbows
        if(elbowLEl) elbowLEl.innerText = data.l_elbow_angle ? `${Math.round(data.l_elbow_angle)}°` : '--°';
        if(elbowREl) elbowREl.innerText = data.r_elbow_angle ? `${Math.round(data.r_elbow_angle)}°` : '--°';
    }
    
    function refreshVideoFeed() {
        const videoFeed = document.getElementById('videoFeed');
        videoFeed.src = "";
        setTimeout(() => {
            videoFeed.src = "/video_feed?" + new Date().getTime();
        }, 100);
        
        // Ensure play button state
        pauseBtn.style.display = 'flex';
        resumeBtn.style.display = 'none';
        
        // Clear File Names if switching source? No, keep it helper
    }

    // Tab Interface logic
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Handle Video Upload
    videoUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        videoFileName.innerText = file.name;
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload_video', { method: 'POST', body: formData });
            const result = await response.json();
            if (result.success) refreshVideoFeed();
        } catch (error) { console.error('Upload failed:', error); }
    });
    
    // Handle Image Upload
    imageUpload.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        imageFileName.innerText = file.name;
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload_image', { method: 'POST', body: formData });
            const result = await response.json();
            if (result.success) refreshVideoFeed();
        } catch (error) { console.error('Upload failed:', error); }
    });

    // Handle YouTube
    youtubeBtn.addEventListener('click', async () => {
        const url = youtubeUrl.value;
        if (!url) {
            alert("Please enter a YouTube URL");
            return;
        }
        
        youtubeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading...';
        
        try {
            const response = await fetch('/set_youtube', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ url: url })
            });
            const result = await response.json();
            if (result.success) {
                refreshVideoFeed();
            } else {
                alert("Failed to load YouTube video. Check URL or logs.");
            }
        } catch (error) { console.error(error); }
        finally {
             youtubeBtn.innerHTML = '<i class="fa-solid fa-play"></i> Load';
        }
    });

    // Handle Camera
    const camSource = document.getElementById('camSource');
    camBtn.addEventListener('click', async () => {
        const sourceVal = camSource.value.trim() || '0';
        try {
            await fetch('/use_camera', { 
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ source: sourceVal })
            });
            refreshVideoFeed();
        } catch (e) { console.error(e); }
    });

    // Handle Accuracy
    accuracySelect.addEventListener('change', async (e) => {
        const complexity = e.target.value;
        try {
            await fetch('/set_accuracy', {
                 method: 'POST',
                 headers: {'Content-Type': 'application/json'},
                 body: JSON.stringify({ complexity: complexity })
            });
        } catch (e) { console.error(e); }
    });
    
    // Playback Controls
    pauseBtn.addEventListener('click', async () => {
        try { 
            await fetch('/control/pause', {method: 'POST'});
            pauseBtn.style.display = 'none';
            resumeBtn.style.display = 'flex';
        } catch(e) {}
    });
    
    resumeBtn.addEventListener('click', async () => {
        try { 
            await fetch('/control/resume', {method: 'POST'});
            pauseBtn.style.display = 'flex';
            resumeBtn.style.display = 'none';
        } catch(e) {}
    });
    
    replayBtn.addEventListener('click', async () => {
        try { 
            await fetch('/control/replay', {method: 'POST'});
            pauseBtn.style.display = 'flex';
            resumeBtn.style.display = 'none';
            // Might need to ensure video reloaded if stream died? Usually just reset pos works.
        } catch(e) {}
    });

    // Handle Reset
    resetBtn.addEventListener('click', async () => {
        try {
            await fetch('/reset', { method: 'POST' });
            updateDashboard({
                step_count: 0,
                cadence: 0,
                symmetry_l: 50,
                symmetry_r: 50,
                l_knee_angle: 0,
                r_knee_angle: 0,
                l_elbow_angle: 0,
                r_elbow_angle: 0
            });
        } catch (error) {
            console.error('Reset failed:', error);
        }
    });

    // Start
    startMetricsPolling();
});
