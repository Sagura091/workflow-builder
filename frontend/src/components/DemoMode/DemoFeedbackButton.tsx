import React, { useState } from 'react';

// Formspree endpoint - configured to send feedback directly to your email
const FORMSPREE_ENDPOINT = 'https://formspree.io/f/mgvkelgj';

const DemoFeedbackButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [email, setEmail] = useState('');
  const [rating, setRating] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Prepare the data to submit
      const formData = {
        rating: rating,
        feedback: feedback,
        email: email || 'Not provided',
        source: 'GitHub Pages Demo',
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        browser: navigator.userAgent.match(/chrome|firefox|safari|edge|opera/i)?.[0] || 'Unknown',
        device: /mobile|android|iphone|ipad|tablet/i.test(navigator.userAgent) ? 'Mobile' : 'Desktop',
        screenSize: `${window.innerWidth}x${window.innerHeight}`,
        referrer: document.referrer || 'Direct',
        feedbackCategory: getFeedbackCategory(feedback)
      };

      // Helper function to categorize feedback based on content
      function getFeedbackCategory(text) {
        const lowerText = text.toLowerCase();
        if (lowerText.includes('bug') || lowerText.includes('error') || lowerText.includes('issue') || lowerText.includes('doesn\'t work')) {
          return 'Bug Report';
        } else if (lowerText.includes('feature') || lowerText.includes('add') || lowerText.includes('would be nice') || lowerText.includes('should have')) {
          return 'Feature Request';
        } else if (lowerText.includes('confus') || lowerText.includes('hard to') || lowerText.includes('difficult') || lowerText.includes('unclear')) {
          return 'Usability Issue';
        } else if (lowerText.includes('like') || lowerText.includes('love') || lowerText.includes('great') || lowerText.includes('good')) {
          return 'Positive Feedback';
        } else {
          return 'General Feedback';
        }
      }

      // Submit to Formspree
      const response = await fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error(`Submission failed: ${response.status} ${response.statusText}`);
      }

      // Log success (for debugging)
      console.log('Feedback submitted successfully:', formData);

      // Show success message
      setSubmitted(true);

      // Reset form after 3 seconds
      setTimeout(() => {
        setIsOpen(false);
        setFeedback('');
        setEmail('');
        setRating(null);
        setSubmitted(false);
      }, 3000);
    } catch (err) {
      console.error('Error submitting feedback:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <button
        className="fixed bottom-4 right-4 z-40 bg-blue-600 text-white rounded-full p-3 shadow-lg hover:bg-blue-700 transition-all duration-200 flex items-center"
        onClick={() => setIsOpen(true)}
      >
        <i className="fas fa-comment-alt mr-2"></i>
        <span>Feedback</span>
      </button>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">
                  Share Your Feedback
                </h2>
                <button
                  className="text-gray-500 hover:text-gray-700"
                  onClick={() => setIsOpen(false)}
                >
                  <i className="fas fa-times"></i>
                </button>
              </div>

              {submitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i className="fas fa-check text-2xl"></i>
                  </div>
                  <h3 className="text-xl font-medium text-gray-800 mb-2">Thank You!</h3>
                  <p className="text-gray-600">
                    Your feedback has been submitted successfully.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit}>
                  {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-red-600 text-sm">
                        <i className="fas fa-exclamation-circle mr-2"></i>
                        {error}
                      </p>
                    </div>
                  )}
                  <div className="mb-6">
                    <label className="block text-gray-700 font-medium mb-2">
                      How would you rate your experience?
                    </label>
                    <div className="flex justify-center space-x-2">
                      {[1, 2, 3, 4, 5].map((value) => (
                        <button
                          key={value}
                          type="button"
                          className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            rating === value
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                          onClick={() => setRating(value)}
                        >
                          {value}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="mb-4">
                    <label className="block text-gray-700 font-medium mb-2" htmlFor="feedback">
                      What do you think of the workflow builder?
                    </label>
                    <textarea
                      id="feedback"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={4}
                      placeholder="Share your thoughts, suggestions, or report issues..."
                      value={feedback}
                      onChange={(e) => setFeedback(e.target.value)}
                      required
                    ></textarea>
                  </div>

                  <div className="mb-6">
                    <label className="block text-gray-700 font-medium mb-2" htmlFor="email">
                      Email (optional)
                    </label>
                    <input
                      type="email"
                      id="email"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="your@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      We'll only use this to follow up on your feedback if needed.
                    </p>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="button"
                      className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 mr-2"
                      onClick={() => setIsOpen(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center"
                      disabled={!feedback || rating === null || isSubmitting}
                    >
                      {isSubmitting ? (
                        <>
                          <i className="fas fa-spinner fa-spin mr-2"></i> Submitting...
                        </>
                      ) : (
                        'Submit Feedback'
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DemoFeedbackButton;
