/**
 * Avatar drawing and animation module
 */

class Avatar {
    constructor(canvasId, gender = 'male') {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gender = gender; // 'male' or 'female'
        this.isSpeaking = false;
        this.mouthOpenness = 0;
        this.targetMouthOpenness = 0;
        this.blinkTimer = 0;
        this.isBlinking = false;
        this.audioLevel = 0;

        // Animation loop
        this.animate();
    }

    /**
     * Set avatar gender
     * @param {string} gender - 'male' or 'female'
     */
    setGender(gender) {
        this.gender = gender;
    }

    /**
     * Set speaking state
     * @param {boolean} speaking - Whether the avatar is speaking
     */
    setSpeaking(speaking) {
        this.isSpeaking = speaking;
        if (!speaking) {
            this.targetMouthOpenness = 0;
        }
    }

    /**
     * Update mouth animation based on audio level
     * @param {number} level - Audio level (0-1)
     */
    updateAudioLevel(level) {
        if (this.isSpeaking) {
            this.targetMouthOpenness = level;
        }
    }

    /**
     * Draw the avatar (routes to male or female)
     */
    draw() {
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;

        // Clear canvas
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, width, height);

        // Center position
        const centerX = width / 2;
        const centerY = height / 2;

        // Draw based on gender
        if (this.gender === 'female') {
            this.drawFemale(ctx, centerX, centerY, width, height);
        } else {
            this.drawMale(ctx, centerX, centerY, width, height);
        }
    }

    /**
     * Draw the male avatar
     */
    drawMale(ctx, centerX, centerY, width, height) {

        // Head
        ctx.fillStyle = '#ffdbac';
        ctx.beginPath();
        ctx.ellipse(centerX, centerY - 50, 100, 120, 0, 0, Math.PI * 2);
        ctx.fill();

        // Neck
        ctx.fillStyle = '#ffdbac';
        ctx.fillRect(centerX - 30, centerY + 60, 60, 40);

        // Shoulders/Body
        ctx.fillStyle = '#4a90e2';
        ctx.beginPath();
        ctx.moveTo(centerX - 80, centerY + 100);
        ctx.lineTo(centerX + 80, centerY + 100);
        ctx.lineTo(centerX + 100, height);
        ctx.lineTo(centerX - 100, height);
        ctx.closePath();
        ctx.fill();

        // Collar
        ctx.strokeStyle = '#3a7bc8';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(centerX - 30, centerY + 100);
        ctx.lineTo(centerX, centerY + 120);
        ctx.lineTo(centerX + 30, centerY + 100);
        ctx.stroke();

        // Hair
        ctx.fillStyle = '#3d2817';
        ctx.beginPath();
        ctx.ellipse(centerX, centerY - 100, 105, 80, 0, 0, Math.PI * 2);
        ctx.fill();

        // Ears
        ctx.fillStyle = '#ffdbac';
        // Left ear
        ctx.beginPath();
        ctx.ellipse(centerX - 100, centerY - 40, 20, 30, 0, 0, Math.PI * 2);
        ctx.fill();
        // Right ear
        ctx.beginPath();
        ctx.ellipse(centerX + 100, centerY - 40, 20, 30, 0, 0, Math.PI * 2);
        ctx.fill();

        // Eyes
        this.drawEyes(ctx, centerX, centerY);

        // Eyebrows
        ctx.strokeStyle = '#3d2817';
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        // Left eyebrow
        ctx.beginPath();
        ctx.moveTo(centerX - 60, centerY - 80);
        ctx.lineTo(centerX - 30, centerY - 85);
        ctx.stroke();
        // Right eyebrow
        ctx.beginPath();
        ctx.moveTo(centerX + 30, centerY - 85);
        ctx.lineTo(centerX + 60, centerY - 80);
        ctx.stroke();

        // Nose
        ctx.strokeStyle = '#d4a574';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY - 30);
        ctx.lineTo(centerX - 8, centerY - 10);
        ctx.moveTo(centerX, centerY - 30);
        ctx.lineTo(centerX + 8, centerY - 10);
        ctx.stroke();

        // Mouth
        this.drawMouth(ctx, centerX, centerY);
    }

    /**
     * Draw the female avatar
     */
    drawFemale(ctx, centerX, centerY, width, height) {
        // Head
        ctx.fillStyle = '#ffdbac';
        ctx.beginPath();
        ctx.ellipse(centerX, centerY - 50, 95, 115, 0, 0, Math.PI * 2);
        ctx.fill();

        // Neck
        ctx.fillStyle = '#ffdbac';
        ctx.fillRect(centerX - 25, centerY + 55, 50, 40);

        // Shoulders/Body
        ctx.fillStyle = '#e91e63'; // Pink/magenta dress
        ctx.beginPath();
        ctx.moveTo(centerX - 75, centerY + 95);
        ctx.lineTo(centerX + 75, centerY + 95);
        ctx.lineTo(centerX + 95, height);
        ctx.lineTo(centerX - 95, height);
        ctx.closePath();
        ctx.fill();

        // Dress neckline
        ctx.strokeStyle = '#c2185b';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(centerX, centerY + 95, 30, Math.PI, Math.PI * 2);
        ctx.stroke();

        // Hair (longer, feminine style)
        ctx.fillStyle = '#5d4037'; // Brown hair

        // Top of hair
        ctx.beginPath();
        ctx.ellipse(centerX, centerY - 105, 110, 85, 0, 0, Math.PI * 2);
        ctx.fill();

        // Left side hair (flowing)
        ctx.beginPath();
        ctx.ellipse(centerX - 85, centerY - 20, 35, 80, -0.3, 0, Math.PI * 2);
        ctx.fill();

        // Right side hair (flowing)
        ctx.beginPath();
        ctx.ellipse(centerX + 85, centerY - 20, 35, 80, 0.3, 0, Math.PI * 2);
        ctx.fill();

        // Bangs
        ctx.beginPath();
        ctx.moveTo(centerX - 80, centerY - 100);
        ctx.quadraticCurveTo(centerX - 60, centerY - 90, centerX - 40, centerY - 85);
        ctx.quadraticCurveTo(centerX - 20, centerY - 90, centerX, centerY - 85);
        ctx.quadraticCurveTo(centerX + 20, centerY - 90, centerX + 40, centerY - 85);
        ctx.quadraticCurveTo(centerX + 60, centerY - 90, centerX + 80, centerY - 100);
        ctx.lineTo(centerX + 80, centerY - 120);
        ctx.lineTo(centerX - 80, centerY - 120);
        ctx.closePath();
        ctx.fill();

        // Ears (smaller, more delicate)
        ctx.fillStyle = '#ffdbac';
        // Left ear
        ctx.beginPath();
        ctx.ellipse(centerX - 95, centerY - 45, 18, 25, 0, 0, Math.PI * 2);
        ctx.fill();
        // Right ear
        ctx.beginPath();
        ctx.ellipse(centerX + 95, centerY - 45, 18, 25, 0, 0, Math.PI * 2);
        ctx.fill();

        // Earrings
        ctx.fillStyle = '#FFD700'; // Gold
        // Left earring
        ctx.beginPath();
        ctx.arc(centerX - 95, centerY - 25, 5, 0, Math.PI * 2);
        ctx.fill();
        // Right earring
        ctx.beginPath();
        ctx.arc(centerX + 95, centerY - 25, 5, 0, Math.PI * 2);
        ctx.fill();

        // Eyes
        this.drawEyes(ctx, centerX, centerY);

        // Eyebrows (thinner, more arched)
        ctx.strokeStyle = '#3d2817';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        // Left eyebrow (arched)
        ctx.beginPath();
        ctx.moveTo(centerX - 60, centerY - 78);
        ctx.quadraticCurveTo(centerX - 45, centerY - 85, centerX - 30, centerY - 80);
        ctx.stroke();
        // Right eyebrow (arched)
        ctx.beginPath();
        ctx.moveTo(centerX + 30, centerY - 80);
        ctx.quadraticCurveTo(centerX + 45, centerY - 85, centerX + 60, centerY - 78);
        ctx.stroke();

        // Eyelashes
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 2;
        // Left eye lashes
        for (let i = 0; i < 5; i++) {
            const angle = -Math.PI / 3 + (i * Math.PI / 12);
            const startX = centerX - 45 + Math.cos(angle) * 15;
            const startY = centerY - 50 + Math.sin(angle) * 18;
            const endX = startX + Math.cos(angle) * 8;
            const endY = startY + Math.sin(angle) * 8;
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        }
        // Right eye lashes
        for (let i = 0; i < 5; i++) {
            const angle = -2 * Math.PI / 3 - (i * Math.PI / 12);
            const startX = centerX + 45 + Math.cos(angle) * 15;
            const startY = centerY - 50 + Math.sin(angle) * 18;
            const endX = startX + Math.cos(angle) * 8;
            const endY = startY + Math.sin(angle) * 8;
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        }

        // Nose (more delicate)
        ctx.strokeStyle = '#d4a574';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(centerX, centerY - 30);
        ctx.lineTo(centerX - 6, centerY - 12);
        ctx.moveTo(centerX, centerY - 30);
        ctx.lineTo(centerX + 6, centerY - 12);
        ctx.stroke();

        // Lips (with color)
        this.drawFemaleMouth(ctx, centerX, centerY);
    }

    /**
     * Draw female mouth with lipstick
     */
    drawFemaleMouth(ctx, centerX, centerY) {
        const mouthY = centerY + 20;

        // Smooth mouth openness transition
        this.mouthOpenness += (this.targetMouthOpenness - this.mouthOpenness) * 0.3;

        if (this.isSpeaking && this.mouthOpenness > 0.1) {
            // Open mouth (ellipse)
            const mouthHeight = 10 + this.mouthOpenness * 30;

            ctx.fillStyle = '#3d2817';
            ctx.beginPath();
            ctx.ellipse(centerX, mouthY + 5, 20, mouthHeight / 2, 0, 0, Math.PI * 2);
            ctx.fill();

            // Tongue (when mouth is open enough)
            if (this.mouthOpenness > 0.3) {
                ctx.fillStyle = '#ff6b6b';
                ctx.beginPath();
                ctx.ellipse(centerX, mouthY + 8, 12, mouthHeight / 3, 0, 0, Math.PI * 2);
                ctx.fill();
            }

            // Lips outline
            ctx.strokeStyle = '#c2185b';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.ellipse(centerX, mouthY + 5, 20, mouthHeight / 2, 0, 0, Math.PI * 2);
            ctx.stroke();
        } else {
            // Closed lips with lipstick
            ctx.fillStyle = '#e91e63';

            // Upper lip
            ctx.beginPath();
            ctx.moveTo(centerX - 25, mouthY);
            ctx.quadraticCurveTo(centerX - 15, mouthY - 5, centerX - 5, mouthY);
            ctx.quadraticCurveTo(centerX, mouthY + 2, centerX + 5, mouthY);
            ctx.quadraticCurveTo(centerX + 15, mouthY - 5, centerX + 25, mouthY);
            ctx.quadraticCurveTo(centerX + 15, mouthY + 8, centerX, mouthY + 10);
            ctx.quadraticCurveTo(centerX - 15, mouthY + 8, centerX - 25, mouthY);
            ctx.fill();

            // Lip shine
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.beginPath();
            ctx.ellipse(centerX, mouthY - 2, 12, 3, 0, 0, Math.PI * 2);
            ctx.fill();

            // Smile curve
            ctx.strokeStyle = '#c2185b';
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.arc(centerX, mouthY - 15, 28, 0.3, Math.PI - 0.3);
            ctx.stroke();
        }
    }

    /**
     * Draw eyes with blinking animation
     */
    drawEyes(ctx, centerX, centerY) {
        const eyeY = centerY - 50;

        if (this.isBlinking) {
            // Draw closed eyes (lines)
            ctx.strokeStyle = '#3d2817';
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            // Left eye
            ctx.beginPath();
            ctx.moveTo(centerX - 55, eyeY);
            ctx.lineTo(centerX - 35, eyeY);
            ctx.stroke();
            // Right eye
            ctx.beginPath();
            ctx.moveTo(centerX + 35, eyeY);
            ctx.lineTo(centerX + 55, eyeY);
            ctx.stroke();
        } else {
            // Draw open eyes
            // Left eye
            ctx.fillStyle = '#FFFFFF';
            ctx.beginPath();
            ctx.ellipse(centerX - 45, eyeY, 15, 18, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#3d2817';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Left pupil
            ctx.fillStyle = '#3d2817';
            ctx.beginPath();
            ctx.arc(centerX - 45, eyeY, 7, 0, Math.PI * 2);
            ctx.fill();

            // Right eye
            ctx.fillStyle = '#FFFFFF';
            ctx.beginPath();
            ctx.ellipse(centerX + 45, eyeY, 15, 18, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#3d2817';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Right pupil
            ctx.fillStyle = '#3d2817';
            ctx.beginPath();
            ctx.arc(centerX + 45, eyeY, 7, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    /**
     * Draw mouth with animation
     */
    drawMouth(ctx, centerX, centerY) {
        const mouthY = centerY + 20;

        // Smooth mouth openness transition
        this.mouthOpenness += (this.targetMouthOpenness - this.mouthOpenness) * 0.3;

        if (this.isSpeaking && this.mouthOpenness > 0.1) {
            // Open mouth (ellipse)
            const mouthHeight = 10 + this.mouthOpenness * 30;

            ctx.fillStyle = '#3d2817';
            ctx.beginPath();
            ctx.ellipse(centerX, mouthY + 5, 25, mouthHeight / 2, 0, 0, Math.PI * 2);
            ctx.fill();

            // Tongue (when mouth is open enough)
            if (this.mouthOpenness > 0.3) {
                ctx.fillStyle = '#ff6b6b';
                ctx.beginPath();
                ctx.ellipse(centerX, mouthY + 8, 15, mouthHeight / 3, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        } else {
            // Closed mouth (smile)
            ctx.strokeStyle = '#3d2817';
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.arc(centerX, mouthY - 10, 30, 0.2, Math.PI - 0.2);
            ctx.stroke();
        }
    }

    /**
     * Animation loop
     */
    animate() {
        // Draw avatar
        this.draw();

        // Handle blinking
        this.blinkTimer++;
        if (this.blinkTimer > 180) { // Blink every ~3 seconds at 60fps
            this.isBlinking = true;
            if (this.blinkTimer > 190) { // Blink duration
                this.isBlinking = false;
                this.blinkTimer = Math.random() * 60; // Random next blink time
            }
        }

        // Random mouth movement when speaking
        if (this.isSpeaking) {
            this.targetMouthOpenness = 0.3 + Math.random() * 0.7;
        }

        // Continue animation
        requestAnimationFrame(() => this.animate());
    }
}

// Export for use in main.js
window.Avatar = Avatar;
