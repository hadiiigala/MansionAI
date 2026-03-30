/**
 * CLIP Evaluation Results Loader
 * This script dynamically loads statistics from the report file and updates the HTML
 */

// Function to parse the report text and extract statistics
function parseReport(reportText) {
    const lines = reportText.split('\n');
    const stats = {};
    const topPairs = [];
    
    let inStatsSection = false;
    let inPairsSection = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Check for section headers
        if (line === 'SUMMARY STATISTICS') {
            inStatsSection = true;
            inPairsSection = false;
            continue;
        } else if (line === 'TOP SIMILAR PAIRS') {
            inStatsSection = false;
            inPairsSection = true;
            continue;
        }
        
        // Parse statistics
        if (inStatsSection) {
            if (line.startsWith('Number of generated images:')) {
                stats.generatedImages = line.split(':')[1].trim();
            } else if (line.startsWith('Number of IKEA images:')) {
                stats.ikeaImages = line.split(':')[1].trim();
            } else if (line.startsWith('Total comparisons:')) {
                stats.totalComparisons = line.split(':')[1].trim();
            } else if (line.startsWith('Mean similarity:')) {
                stats.meanSimilarity = line.split(':')[1].trim();
            } else if (line.startsWith('Standard deviation:')) {
                stats.stdDeviation = line.split(':')[1].trim();
            } else if (line.startsWith('Min similarity:')) {
                stats.minSimilarity = line.split(':')[1].trim();
            } else if (line.startsWith('Max similarity:')) {
                stats.maxSimilarity = line.split(':')[1].trim();
            }
        }
        
        // Parse top pairs
        if (inPairsSection && line.match(/^\d+\./)) {
            const similarityMatch = line.match(/Similarity: ([\d.]+)/);
            const generatedMatch = lines[i + 1]?.match(/Generated: (.+)/);
            const ikeaMatch = lines[i + 2]?.match(/IKEA: (.+)/);
            
            if (similarityMatch && generatedMatch && ikeaMatch) {
                topPairs.push({
                    rank: topPairs.length + 1,
                    similarity: similarityMatch[1],
                    generated: generatedMatch[1],
                    ikea: ikeaMatch[1]
                });
                i += 2; // Skip the next two lines as we've already processed them
            }
        }
    }
    
    return { stats, topPairs };
}

// Function to update the statistics table
function updateStatistics(stats) {
    if (stats.generatedImages) {
        document.getElementById('generated-images-count').textContent = stats.generatedImages;
    }
    if (stats.ikeaImages) {
        document.getElementById('ikea-images-count').textContent = stats.ikeaImages;
    }
    if (stats.totalComparisons) {
        document.getElementById('total-comparisons').textContent = stats.totalComparisons;
    }
    if (stats.meanSimilarity) {
        document.getElementById('mean-similarity').textContent = stats.meanSimilarity;
    }
    if (stats.stdDeviation) {
        document.getElementById('std-deviation').textContent = stats.stdDeviation;
    }
    if (stats.minSimilarity) {
        document.getElementById('min-similarity').textContent = stats.minSimilarity;
    }
    if (stats.maxSimilarity) {
        document.getElementById('max-similarity').textContent = stats.maxSimilarity;
    }
}

// Function to update the top pairs section
function updateTopPairs(pairs) {
    const container = document.getElementById('top-pairs-container');
    
    if (pairs.length === 0) {
        container.innerHTML = '<div class="loading">No similar pairs found.</div>';
        return;
    }
    
    // Clear existing content
    container.innerHTML = '';
    
    // Add new pairs
    pairs.forEach((pair, index) => {
        const pairElement = document.createElement('div');
        pairElement.className = 'pair';
        pairElement.innerHTML = `
            <h4>${index + 1}. Similarity: ${pair.similarity}</h4>
            <p><strong>Generated:</strong> ${pair.generated}</p>
            <p><strong>IKEA:</strong> ${pair.ikea}</p>
        `;
        container.appendChild(pairElement);
    });
}

// Function to load and display the report
async function loadReport() {
    try {
        const response = await fetch('clip_eval_results/clip_eval_report.txt');
        if (!response.ok) {
            throw new Error('Report file not found');
        }
        
        const reportText = await response.text();
        const { stats, topPairs } = parseReport(reportText);
        
        // Update the UI with actual data
        updateStatistics(stats);
        updateTopPairs(topPairs);
        
    } catch (error) {
        console.warn('Could not load report file:', error);
        // Display error message
        const container = document.getElementById('top-pairs-container');
        container.innerHTML = '<div class="loading">Report data not available. Run the evaluation scripts to generate results.</div>';
    }
}

// Load the report when the page loads
document.addEventListener('DOMContentLoaded', loadReport);