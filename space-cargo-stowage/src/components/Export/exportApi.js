import axios from 'axios';

const API_URL = 'http://localhost:8000';

export async function exportArrangements(format = 'csv') {
    try {
        const response = await axios.get(`${API_URL}/api/export/arrangements`, {
            params: { format },
            responseType: 'blob' // Important for file downloads
        });
        
        // Create download link
        const blob = new Blob([response.data], { 
            type: format === 'csv' ? 'text/csv' : 'application/json' 
        });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `cargo_arrangements.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        return { success: true, message: 'Arrangements exported successfully' };
    } catch (error) {
        console.error('Error exporting arrangements:', error);
        throw error;
    }
}

export async function exportWasteReport(wasteItems, format = 'csv') {
    try {
        // For client-side CSV generation as fallback
        if (format === 'csv') {
            const headers = ['ID', 'Item Name', 'Container', 'Reason', 'Date Identified'];
            const csvData = [
                headers.join(','),
                ...wasteItems.map(item => 
                    [
                        item.itemId, 
                        `"${item.name}"`, // Wrap in quotes to handle commas in names
                        item.containerId, 
                        `"${item.reason}"`,
                        item.dateIdentified || new Date().toISOString().split('T')[0]
                    ].join(',')
                )
            ].join('\n');

            const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `waste_report_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            return { success: true, message: 'Waste report exported successfully' };
        }
        
        return { success: false, message: 'Unsupported format' };
    } catch (error) {
        console.error('Error exporting waste report:', error);
        throw error;
    }
}
