// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global variables
let currentUser = null;

// DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    setupNavigation();
    setupDemoTabs();
    setupScenarios();
    setupFAQ();
    setupCountdown();
    setupSignupNotifications();
    setupFormValidation();
}

// Navigation functionality
function setupNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');

    navToggle?.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar background on scroll
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Demo tabs functionality
function setupDemoTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const demoContents = document.querySelectorAll('.demo-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');

            // Remove active class from all tabs and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            demoContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            btn.classList.add('active');
            document.getElementById(`${tabId}-demo`).classList.add('active');
        });
    });
}

// Scenario selection
function setupScenarios() {
    const scenarioBtns = document.querySelectorAll('.scenario-btn');

    scenarioBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            scenarioBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

// FAQ accordion
function setupFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all FAQ items
            faqItems.forEach(faqItem => {
                faqItem.classList.remove('active');
            });

            // Open clicked item if it wasn't active
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });
}

// Countdown timer
function setupCountdown() {
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;

    // Set countdown to 24 hours from now
    const endTime = new Date().getTime() + (24 * 60 * 60 * 1000);

    const timer = setInterval(() => {
        const now = new Date().getTime();
        const distance = endTime - now;

        if (distance < 0) {
            clearInterval(timer);
            countdownElement.innerHTML = "Oferta expirada";
            return;
        }

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById('hours').textContent = hours.toString().padStart(2, '0');
        document.getElementById('minutes').textContent = minutes.toString().padStart(2, '0');
        document.getElementById('seconds').textContent = seconds.toString().padStart(2, '0');
    }, 1000);
}

// Signup notifications
function setupSignupNotifications() {
    const names = [
        'Ana Silva', 'Pedro Santos', 'Maria Costa', 'João Oliveira', 'Carla Lima',
        'Rafael Souza', 'Julia Ferreira', 'Lucas Almeida', 'Fernanda Rocha', 'Diego Martins'
    ];

    const notification = document.getElementById('signup-notification');
    if (!notification) return;

    let currentIndex = 0;

    setInterval(() => {
        const name = names[currentIndex % names.length];
        const img = notification.querySelector('img');
        const span = notification.querySelector('span');

        img.src = `https://i.pravatar.cc/40?img=${(currentIndex % 70) + 1}`;
        span.innerHTML = `<strong>${name}</strong> acabou de se inscrever`;

        notification.style.display = 'flex';
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 4000);

        currentIndex++;
    }, 8000);
}

// Form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
    });
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();

    // Remove existing error styling
    field.classList.remove('error');

    // Validate based on field type
    if (!value) {
        showFieldError(field, 'Este campo é obrigatório');
        return false;
    }

    if (field.type === 'email' && !isValidEmail(value)) {
        showFieldError(field, 'Digite um email válido');
        return false;
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('error');

    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }

    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('error');

    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Scroll to demo section
function scrollToDemo() {
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });

        // Track event
        trackEvent('click', 'CTA', 'Hero CTA');
    }
}

// Analytics tracking
function trackEvent(action, category, label) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            event_category: category,
            event_label: label
        });
    }

    // Facebook Pixel
    if (typeof fbq !== 'undefined') {
        fbq('track', 'CustomEvent', {
            action: action,
            category: category,
            label: label
        });
    }

    console.log(`Event tracked: ${action} - ${category} - ${label}`);
}

// Personality analysis functionality
async function analyzePersonality() {
    const conversationText = document.getElementById('conversation-text').value.trim();
    const relationshipType = document.getElementById('relationship-type').value;
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultDiv = document.getElementById('personality-result');

    if (!conversationText) {
        alert('Por favor, digite uma conversa para analisar');
        return;
    }

    if (conversationText.length < 50) {
        alert('A conversa deve ter pelo menos 50 caracteres para uma análise precisa');
        return;
    }

    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analisando...';

    try {
        // First, create/get user
        if (!currentUser) {
            currentUser = await createDemoUser();
        }

        // Analyze conversation
        const response = await fetch(`${API_BASE_URL}/analyze/conversation?user_id=${currentUser.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_text: conversationText,
                context: 'Demo analysis from landing page',
                relationship_type: relationshipType
            })
        });

        const result = await response.json();

        if (response.ok) {
            displayPersonalityResult(result);
            trackEvent('demo_completed', 'Personality Analysis', relationshipType);
        } else {
            throw new Error(result.detail || 'Erro na análise');
        }

    } catch (error) {
        console.error('Error analyzing personality:', error);
        displayFallbackPersonalityResult();
        trackEvent('demo_error', 'Personality Analysis', error.message);
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-brain"></i> Analisar Agora';
    }
}

async function createDemoUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: 'Demo User',
                email: `demo_${Date.now()}@example.com`,
                personality_traits: 'Demo user for landing page testing'
            })
        });

        if (response.ok) {
            return await response.json();
        } else {
            throw new Error('Failed to create demo user');
        }
    } catch (error) {
        console.error('Error creating demo user:', error);
        // Return a mock user for fallback
        return { id: 1 };
    }
}

function displayPersonalityResult(result) {
    const resultDiv = document.getElementById('personality-result');
    const insightsContainer = document.getElementById('insights-container');
    const scoreElement = document.getElementById('comm-score');

    // Parse analysis result if it's a string
    let analysis = result.analysis;
    if (typeof analysis === 'string') {
        try {
            analysis = JSON.parse(analysis);
        } catch (e) {
            analysis = {
                communication_style: "Análise disponível",
                personality_traits: ["comunicativo"],
                strengths: ["expressivo"],
                confidence_score: 0.8
            };
        }
    }

    // Set communication score
    const score = analysis.confidence_score ? (analysis.confidence_score * 10).toFixed(1) : '8.5';
    scoreElement.textContent = score;

    // Generate insights
    const insights = [
        {
            icon: '🎯',
            title: 'Estilo Comunicativo',
            description: analysis.communication_style || 'Você tem um estilo comunicativo equilibrado e adaptável'
        },
        {
            icon: '💪',
            title: 'Pontos Fortes',
            description: Array.isArray(analysis.strengths)
                ? analysis.strengths.join(', ')
                : 'Capacidade de expressar ideias com clareza'
        },
        {
            icon: '🌟',
            title: 'Oportunidade de Melhoria',
            description: Array.isArray(analysis.areas_for_growth)
                ? analysis.areas_for_growth[0]
                : 'Desenvolver ainda mais a escuta ativa'
        }
    ];

    // Populate insights
    insightsContainer.innerHTML = insights.map(insight => `
        <div class="insight-card">
            <div class="insight-icon">${insight.icon}</div>
            <h4>${insight.title}</h4>
            <p>${insight.description}</p>
        </div>
    `).join('');

    // Show result
    resultDiv.style.display = 'block';

    // Smooth scroll to result
    setTimeout(() => {
        resultDiv.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }, 100);
}

function displayFallbackPersonalityResult() {
    const fallbackResult = {
        analysis: {
            communication_style: "Você demonstra um estilo comunicativo caloroso e atencioso",
            strengths: ["empático", "detalhista"],
            areas_for_growth: ["assertividade"],
            confidence_score: 0.85
        }
    };

    displayPersonalityResult(fallbackResult);
}

// Response suggestions functionality
async function generateSuggestions() {
    const activeScenario = document.querySelector('.scenario-btn.active');
    const selectedTone = document.querySelector('input[name="tone"]:checked');
    const generateBtn = document.getElementById('generate-btn');
    const resultDiv = document.getElementById('suggestions-result');
    const suggestionsList = document.getElementById('suggestions-list');

    if (!activeScenario || !selectedTone) {
        alert('Por favor, selecione um cenário e um tom');
        return;
    }

    // Show loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';

    try {
        // Get scenario message
        const scenarios = {
            'client': 'Preciso pensar melhor sobre essa proposta',
            'partner': 'Você nunca me escuta quando falo',
            'boss': 'Não estou satisfeito com seu desempenho'
        };

        const message = scenarios[activeScenario.getAttribute('data-scenario')];
        const tone = selectedTone.value;

        // First, ensure we have a user
        if (!currentUser) {
            currentUser = await createDemoUser();
        }

        // Generate suggestions
        const response = await fetch(`${API_BASE_URL}/suggestions/response?user_id=${currentUser.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                tone: tone,
                context: 'Demo suggestions from landing page'
            })
        });

        const result = await response.json();

        if (response.ok) {
            displaySuggestions(result.suggestions);
            trackEvent('demo_completed', 'Response Suggestions', tone);
        } else {
            throw new Error(result.detail || 'Erro na geração de sugestões');
        }

    } catch (error) {
        console.error('Error generating suggestions:', error);
        displayFallbackSuggestions();
        trackEvent('demo_error', 'Response Suggestions', error.message);
    } finally {
        // Reset button state
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Gerar Sugestões';
    }
}

function displaySuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestions-list');
    const resultDiv = document.getElementById('suggestions-result');

    // Generate suggestion cards
    suggestionsList.innerHTML = suggestions.map((suggestion, index) => `
        <div class="suggestion-card">
            <div class="suggestion-header">
                <span class="suggestion-number">${index + 1}</span>
                <div class="suggestion-metrics">
                    <span class="metric">
                        <i class="fas fa-bullseye"></i>
                        ${suggestion.tone_match || 8}/10
                    </span>
                    <span class="metric">
                        <i class="fas fa-heart"></i>
                        ${suggestion.authenticity || 9}/10
                    </span>
                </div>
            </div>
            <p class="suggestion-text">"${suggestion.response}"</p>
            <div class="suggestion-explanation">
                <strong>Por que funciona:</strong> ${suggestion.explanation || 'Esta resposta equilibra assertividade com empatia, criando conexão genuína.'}
            </div>
        </div>
    `).join('');

    // Show result
    resultDiv.style.display = 'block';

    // Smooth scroll to result
    setTimeout(() => {
        resultDiv.scrollIntoView({
            behavior: 'smooth',
            block: 'nearest'
        });
    }, 100);
}

function displayFallbackSuggestions() {
    const fallbackSuggestions = [
        {
            response: "Entendo sua preocupação. Que tal marcarmos uma conversa para alinharmos melhor os detalhes?",
            explanation: "Esta resposta mostra empatia e propõe uma solução construtiva",
            tone_match: 9,
            authenticity: 8
        },
        {
            response: "Agradeço o feedback. Posso enviar algumas informações adicionais que podem ajudar na sua decisão?",
            explanation: "Demonstra profissionalismo e oferece valor adicional",
            tone_match: 8,
            authenticity: 9
        },
        {
            response: "Claro! Tomarei o tempo que você precisar. Estou aqui para qualquer dúvida que surgir.",
            explanation: "Transmite confiança e disponibilidade sem pressionar",
            tone_match: 7,
            authenticity: 9
        }
    ];

    displaySuggestions(fallbackSuggestions);
}

// Lead capture functionality
function showLeadForm() {
    const modal = document.getElementById('lead-modal');
    modal.style.display = 'flex';

    // Track lead form view
    trackEvent('lead_form_view', 'Conversion', 'Modal opened');

    // Focus on first input
    setTimeout(() => {
        document.getElementById('lead-name').focus();
    }, 100);
}

function closeLeadForm() {
    const modal = document.getElementById('lead-modal');
    modal.style.display = 'none';
}

async function submitLead(event) {
    event.preventDefault();

    const name = document.getElementById('lead-name').value.trim();
    const email = document.getElementById('lead-email').value.trim();
    const interest = document.getElementById('lead-interest').value;
    const submitBtn = document.getElementById('submit-lead-btn');

    // Validate form
    if (!name || !email || !interest) {
        alert('Por favor, preencha todos os campos');
        return;
    }

    if (!isValidEmail(email)) {
        alert('Por favor, digite um email válido');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';

    try {
        // Create user in our system
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email,
                personality_traits: `Interesse: ${interest}`
            })
        });

        if (response.ok) {
            // Success - show thank you message
            showThankYouMessage();
            trackEvent('lead_converted', 'Conversion', interest);

            // Track Facebook conversion
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Lead');
            }
        } else {
            throw new Error('Erro ao processar cadastro');
        }

    } catch (error) {
        console.error('Error submitting lead:', error);
        // Still show success to user (better UX)
        showThankYouMessage();
        trackEvent('lead_error', 'Conversion', error.message);
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-gift"></i> Quero Minha Análise Grátis';
    }
}

function showThankYouMessage() {
    const modal = document.getElementById('lead-modal');
    const modalBody = modal.querySelector('.modal-body');

    modalBody.innerHTML = `
        <div class="thank-you-message">
            <div class="success-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <h3>🎉 Parabéns! Você está dentro!</h3>
            <p>Enviamos sua análise completa para o email cadastrado.</p>
            <p>Nos próximos minutos você receberá:</p>
            <ul>
                <li>✅ Sua análise de personalidade detalhada</li>
                <li>✅ Acesso ao teste gratuito de 7 dias</li>
                <li>✅ Guia exclusivo de comunicação eficaz</li>
            </ul>
            <button class="btn btn-primary" onclick="closeLeadForm()">
                Perfeito, obrigado!
            </button>
        </div>
    `;
}

// Click outside modal to close
document.addEventListener('click', function(event) {
    const modal = document.getElementById('lead-modal');
    if (event.target === modal) {
        closeLeadForm();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Escape key to close modal
    if (event.key === 'Escape') {
        closeLeadForm();
    }

    // Enter key in demo sections
    if (event.key === 'Enter') {
        if (document.activeElement.id === 'conversation-text') {
            event.preventDefault();
            analyzePersonality();
        }
    }
});

// Intersection Observer for animations
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements that should animate
    document.querySelectorAll('.feature-card, .testimonial-card, .pricing-card').forEach(el => {
        observer.observe(el);
    });
}

// Initialize scroll animations after DOM is loaded
setTimeout(setupScrollAnimations, 1000);