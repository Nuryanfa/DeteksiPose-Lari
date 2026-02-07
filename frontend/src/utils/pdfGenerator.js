import jsPDF from 'jspdf';
import 'jspdf-autotable';

export const generatePDF = (stats, user) => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;

    // --- Helper Functions ---
    const addText = (text, x, y, size = 12, style = 'normal', color = [0, 0, 0], align = 'left') => {
        doc.setFontSize(size);
        doc.setFont('helvetica', style); // Use standard font
        doc.setTextColor(...color);
        doc.text(text, x, y, { align: align });
    };

    const drawLine = (y, color = [200, 200, 200]) => {
        doc.setDrawColor(...color);
        doc.setLineWidth(0.5);
        doc.line(margin, y, pageWidth - margin, y);
    };

    // --- Header ---
    // Logo Placeholder (Blue Square)
    doc.setFillColor(37, 99, 235); // Clinical Blue
    doc.rect(margin, margin, 15, 15, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text("SSTS", margin + 7.5, margin + 10, { align: "center" });

    // Title
    addText("Clinical Biomechanics Report", margin + 20, margin + 6, 18, 'bold', [30, 41, 59]);
    addText("Smart Sprint Training System", margin + 20, margin + 12, 10, 'normal', [100, 116, 139]);

    // Date
    const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    addText(today, pageWidth - margin, margin + 10, 10, 'normal', [100, 116, 139], 'right');

    drawLine(margin + 20);

    // --- Patient Info ---
    let courY = margin + 35;
    addText("PATIENT DETAILS", margin, courY, 10, 'bold', [100, 116, 139]);
    courY += 8;
    addText(`Name: ${user?.full_name || 'Unknown Athlete'}`, margin, courY, 12, 'bold');
    addText(`Role: ${user?.role || 'Athlete'}`, pageWidth / 2, courY, 12, 'normal');
    // addText(`Session ID: #SESS-${Date.now().toString().slice(-6)}`, pageWidth - margin, courY, 12, 'normal', [0,0,0], 'right'); // Optional

    courY += 15;
    drawLine(courY);

    // --- Technique Score ---
    courY += 20;
    // Score Box
    doc.setFillColor(248, 250, 252); // Gray 50
    doc.roundedRect(margin, courY, pageWidth - (margin * 2), 40, 3, 3, 'F');
    
    addText("TECHNIQUE SCORE", pageWidth / 2, courY + 10, 10, 'bold', [100, 116, 139], 'center');
    
    const score = stats?.score || 0;
    let scoreColor = [37, 99, 235]; // Blue
    if (score < 60) scoreColor = [239, 68, 68]; // Red
    else if (score < 80) scoreColor = [245, 158, 11]; // Amber

    addText(`${score}`, pageWidth / 2, courY + 25, 30, 'bold', scoreColor, 'center');
    addText("/ 100", pageWidth / 2, courY + 32, 12, 'normal', [148, 163, 184], 'center'); // Offset slightly

    courY += 50;

    // --- Key Metrics Table ---
    addText("BIOMECHANICAL ANALYSIS", margin, courY, 10, 'bold', [100, 116, 139]);
    courY += 5;

    const tableData = [
        ['Cadence', `${stats?.cadence || 0} spm`, '170 - 190 spm', stats?.cadence < 160 ? 'Low' : 'Optimal'],
        ['Stride Length', `${stats?.stride_length || 0} m`, '> 1.2 m', '-'],
        ['Ground Contact Time', `${stats?.gct || 0} ms`, '< 200 ms', stats?.gct > 250 ? 'High Risk' : 'Good'],
        ['Left/Right Symmetry', `L: ${stats?.symmetry?.left || 50}% / R: ${stats?.symmetry?.right || 50}%`, '50% / 50%', (Math.abs((stats?.symmetry?.left || 50) - 50) > 5) ? 'Asymmetric' : 'Balanced'],
        ['Swing Mechanics Error', `${stats?.errors?.swing_mechanics || 0}%`, '< 10%', '-'],
        ['Hip Stability Error', `${stats?.errors?.hip_stability || 0}%`, '< 10%', '-'],
    ];

    doc.autoTable({
        startY: courY,
        head: [['Metric', 'Measured Value', 'Target Range', 'Status']],
        body: tableData,
        theme: 'grid',
        headStyles: { fillColor: [37, 99, 235], textColor: 255, fontStyle: 'bold' },
        styles: { fontSize: 10, cellPadding: 4 },
        columnStyles: {
            0: { fontStyle: 'bold' },
            3: { fontStyle: 'normal' } // Could add custom cell coloring logic here if needed, but keeping simple for v1
        },
        margin: { left: margin, right: margin }
    });

    courY = doc.lastAutoTable.finalY + 20;

    // --- Recommendations ---
    // Check if we have space, else new page
    if (courY > pageHeight - 60) {
        doc.addPage();
        courY = margin;
    }

    addText("CLINICAL RECOMMENDATIONS", margin, courY, 10, 'bold', [100, 116, 139]);
    courY += 10;

    const feedback = stats?.feedback || ["No specific data available yet. Please complete a session."];
    
    feedback.forEach((msg) => {
        // Simple bullet point handling
        const cleanMsg = msg.replace(/✅|⚠️|❌/g, '').trim();
        doc.setFillColor(37, 99, 235);
        doc.circle(margin + 2, courY - 1, 1, 'F');
        
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        doc.setTextColor(51, 65, 85);
        
        // Split text to fit width
        const splitText = doc.splitTextToSize(cleanMsg, pageWidth - (margin * 2) - 10);
        doc.text(splitText, margin + 8, courY);
        courY += (splitText.length * 6) + 4; 
    });

    // --- Footer ---
    const pageCount = doc.internal.getNumberOfPages();
    for(let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text(`Generated by SSTS AI - Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
    }

    // Save
    doc.save(`SSTS_Report_${user?.full_name?.replace(/\s+/g, '_') || 'Patient'}_${Date.now()}.pdf`);
};
