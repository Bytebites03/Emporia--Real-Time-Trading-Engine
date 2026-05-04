// Trading Engine Frontend Client
// Get auth token
const AUTH_TOKEN = localStorage.getItem('access_token');
const USER_ID = localStorage.getItem('user_id');

if (!AUTH_TOKEN) {
    window.location.href = 'login.html';
}

// Add auth header to all fetch requests
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    if (!options.headers) options.headers = {};
    options.headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
    return originalFetch(url, options);
};

// Update WebSocket connection to use user ID
const wsUrl = `ws://localhost:8000/ws/${USER_ID}`;
class TradingClient {
    constructor() {
        this.ws = null;
        this.userId = 'user_' + Math.random().toString(36).substr(2, 9);
        this.currentPrice = 50000;
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.bindEvents();
        this.startPriceSimulation();
    }
    
    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/${this.userId}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }
    
    handleWebSocketMessage(data) {
        switch(data.type) {
            case 'init':
                this.updateOrderBook(data.orderbook);
                this.updateTrades(data.trades);
                this.updatePortfolio(data.portfolio);
                break;
            case 'orderbook_update':
                this.updateOrderBook(data.orderbook);
                break;
            case 'order_update':
                this.addTrade(data.trades);
                break;
            case 'market_data':
                this.updateCurrentPrice(data.price);
                break;
        }
    }
    
    bindEvents() {
        // Buy/Sell toggle
        document.getElementById('buyBtn').addEventListener('click', () => {
            document.getElementById('buyBtn').classList.add('active');
            document.getElementById('sellBtn').classList.remove('active');
            document.getElementById('side').value = 'buy';
        });
        
        document.getElementById('sellBtn').addEventListener('click', () => {
            document.getElementById('sellBtn').classList.add('active');
            document.getElementById('buyBtn').classList.remove('active');
            document.getElementById('side').value = 'sell';
        });
        
        // Order type toggle
        document.getElementById('orderType').addEventListener('change', (e) => {
            const priceGroup = document.getElementById('priceGroup');
            if (e.target.value === 'market') {
                priceGroup.style.display = 'none';
            } else {
                priceGroup.style.display = 'block';
            }
        });
        
        // Calculate total value
        document.getElementById('quantity').addEventListener('input', () => this.calculateTotal());
        document.getElementById('price').addEventListener('input', () => this.calculateTotal());
        
        // Form submission
        document.getElementById('orderForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.placeOrder();
        });
    }
    
    calculateTotal() {
        const quantity = parseFloat(document.getElementById('quantity').value) || 0;
        const price = parseFloat(document.getElementById('price').value) || this.currentPrice;
        const total = quantity * price;
        document.getElementById('totalValue').value = total.toFixed(2);
    }
    
    async placeOrder() {
        const side = document.getElementById('side').value;
        const type = document.getElementById('orderType').value;
        const quantity = parseFloat(document.getElementById('quantity').value);
        const price = type === 'limit' ? parseFloat(document.getElementById('price').value) : 0;
        
        if (!quantity || quantity <= 0) {
            alert('Please enter a valid quantity');
            return;
        }
        
        if (type === 'limit' && (!price || price <= 0)) {
            alert('Please enter a valid price');
            return;
        }
        
        const order = {
            side: side,
            type: type,
            quantity: quantity,
            price: price,
            user_id: this.userId
        };
        
        try {
            const response = await fetch('http://localhost:8000/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(order)
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Order placed:', result);
                document.getElementById('orderForm').reset();
                this.showNotification('Order placed successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.detail || 'Order failed', 'error');
            }
        } catch (error) {
            console.error('Error placing order:', error);
            this.showNotification('Failed to place order', 'error');
        }
    }
    
    updateOrderBook(orderbook) {
        if (!orderbook) return;
        
        // Update asks (sell orders)
        const asksContainer = document.getElementById('asks');
        asksContainer.innerHTML = '';
        orderbook.asks.slice(0, 10).forEach(([price, size]) => {
            const total = price * size;
            const row = document.createElement('div');
            row.className = 'ask-row';
            row.innerHTML = `
                <span>${price.toFixed(2)}</span>
                <span>${size.toFixed(4)}</span>
                <span>${total.toFixed(2)}</span>
            `;
            asksContainer.appendChild(row);
        });
        
        // Update bids (buy orders)
        const bidsContainer = document.getElementById('bids');
        bidsContainer.innerHTML = '';
        orderbook.bids.slice(0, 10).forEach(([price, size]) => {
            const total = price * size;
            const row = document.createElement('div');
            row.className = 'bid-row';
            row.innerHTML = `
                <span>${price.toFixed(2)}</span>
                <span>${size.toFixed(4)}</span>
                <span>${total.toFixed(2)}</span>
            `;
            bidsContainer.appendChild(row);
        });
        
        // Update spread
        const bestBid = orderbook.bids[0] ? orderbook.bids[0][0] : 0;
        const bestAsk = orderbook.asks[0] ? orderbook.asks[0][0] : 0;
        const spread = bestAsk - bestBid;
        const spreadPercent = (spread / bestAsk) * 100;
        
        document.getElementById('spread').innerHTML = `
            Spread: ${spread.toFixed(2)} (${spreadPercent.toFixed(2)}%)
            <br>Bid: ${bestBid.toFixed(2)} | Ask: ${bestAsk.toFixed(2)}
        `;
    }
    
    updateTrades(trades) {
        const tradesContainer = document.getElementById('trades');
        tradesContainer.innerHTML = '';
        
        trades.slice().reverse().forEach(trade => {
            const row = document.createElement('div');
            row.className = 'trade-row';
            const time = new Date(trade.timestamp).toLocaleTimeString();
            row.innerHTML = `
                <span>${time}</span>
                <span class="${trade.side === 'buy' ? 'trade-buy' : 'trade-sell'}">${trade.price.toFixed(2)}</span>
                <span>${trade.quantity.toFixed(4)}</span>
            `;
            tradesContainer.appendChild(row);
        });
    }
    
    addTrade(trades) {
        if (!trades || trades.length === 0) return;
        
        const tradesContainer = document.getElementById('trades');
        trades.forEach(trade => {
            const row = document.createElement('div');
            row.className = 'trade-row';
            const time = new Date(trade.timestamp).toLocaleTimeString();
            row.innerHTML = `
                <span>${time}</span>
                <span class="trade-buy">${trade.price.toFixed(2)}</span>
                <span>${trade.quantity.toFixed(4)}</span>
            `;
            tradesContainer.insertBefore(row, tradesContainer.firstChild);
            
            // Keep only last 50 trades
            if (tradesContainer.children.length > 50) {
                tradesContainer.removeChild(tradesContainer.lastChild);
            }
        });
        
        // Update current price
        if (trades.length > 0) {
            this.updateCurrentPrice(trades[trades.length - 1].price);
        }
    }
    
    async updatePortfolio(portfolio) {
        document.getElementById('cashBalance').innerText = `$${portfolio.cash.toFixed(2)}`;
        document.getElementById('btcBalance').innerText = `${portfolio.crypto.toFixed(4)} BTC`;
        document.getElementById('totalValueDisplay').innerText = `$${portfolio.total_value.toFixed(2)}`;
    }
    
    updateCurrentPrice(price) {
        this.currentPrice = price;
        document.getElementById('currentPrice').innerText = `$${price.toFixed(2)}`;
        this.calculateTotal();
    }
    
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connectionStatus');
        const dot = statusEl.querySelector('.status-dot');
        
        if (connected) {
            dot.classList.add('connected');
            statusEl.innerHTML = '<span class="status-dot connected"></span> Connected';
        } else {
            dot.classList.remove('connected');
            statusEl.innerHTML = '<span class="status-dot"></span> Connecting...';
        }
    }
    
    showNotification(message, type) {
        // Simple alert for now, can be enhanced with toast notifications
        if (type === 'error') {
            alert('❌ ' + message);
        } else {
            console.log('✅', message);
        }
    }
    
    startPriceSimulation() {
        // Initial portfolio fetch
        setInterval(async () => {
            try {
                const response = await fetch(`http://localhost:8000/portfolio/${this.userId}`);
                if (response.ok) {
                    const portfolio = await response.json();
                    this.updatePortfolio(portfolio);
                }
            } catch (error) {
                console.error('Error fetching portfolio:', error);
            }
        }, 2000);
    }
}

// Initialize the trading client
const client = new TradingClient();

// Add after your existing TradingClient class

class PriceChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
        this.priceHistory = [];
        this.init();
    }
    
    init() {
        if (!this.canvas) return;
        
        this.chart = new Chart(this.canvas, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'BTC/USD',
                    data: [],
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: '#e0e0e0' } },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { grid: { color: '#2a2f4a' }, ticks: { color: '#e0e0e0' } },
                    y: { grid: { color: '#2a2f4a' }, ticks: { color: '#e0e0e0' } }
                }
            }
        });
    }
    
    addPrice(price, timestamp) {
        this.priceHistory.push({ price, timestamp });
        if (this.priceHistory.length > 100) this.priceHistory.shift();
        
        // Update chart with simplified data (since candlestick requires OHLC)
        if (this.chart) {
            this.chart.data.datasets[0].data = this.priceHistory.map(p => ({
                x: p.timestamp,
                y: p.price
            }));
            this.chart.update();
        }
    }
}

// Add volume profile visualization
class VolumeProfile {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.volumeLevels = {};
    }
    
    addTrade(price, volume) {
        const priceLevel = Math.floor(price / 100) * 100;
        if (!this.volumeLevels[priceLevel]) {
            this.volumeLevels[priceLevel] = 0;
        }
        this.volumeLevels[priceLevel] += volume;
        this.render();
    }
    
    render() {
        if (!this.container) return;
        
        const maxVolume = Math.max(...Object.values(this.volumeLevels));
        const levels = Object.entries(this.volumeLevels)
            .sort((a, b) => parseFloat(b[0]) - parseFloat(a[0]))
            .slice(0, 20);
        
        this.container.innerHTML = '<h3>Volume Profile</h3>';
        levels.forEach(([price, volume]) => {
            const width = (volume / maxVolume) * 100;
            const div = document.createElement('div');
            div.className = 'volume-bar';
            div.innerHTML = `
                <span class="volume-price">$${price}</span>
                <div class="volume-bar-fill" style="width: ${width}%"></div>
                <span class="volume-value">${volume.toFixed(2)} BTC</span>
            `;
            this.container.appendChild(div);
        });
    }
}

// Initialize chart when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.priceChart = new PriceChart('priceChart');
    window.volumeProfile = new VolumeProfile('volumeProfile');
});