import api from './api';

const authService = {
  register: async (fullName, email, password) => {
    const response = await api.post('/api/auth/register', {
      full_name: fullName,
      email,
      password,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/api/auth/logout');
    return response.data;
  },

  requestPasswordReset: async (email) => {
    const response = await api.post('/api/auth/password-reset', {
      email,
    });
    return response.data;
  },

  confirmPasswordReset: async (token, newPassword) => {
    const response = await api.post('/api/auth/password-reset/confirm', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },
};

export default authService;
