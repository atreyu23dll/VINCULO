import Constants from 'expo-constants';

// Extraemos la IP de la variable de entorno o usamos localhost por defecto
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
const MY_IP = API_URL.split('://')[1].split(':')[0];

export const KEYCLOAK_CONFIG = {
    realm: 'Vinculo',
    clientId: 'vinculo-app',
    url: `http://${MY_IP}:8080`, // Dinámico basado en la IP detectada
};

export const AUTH_CONFIG = {
    discovery: {
        authorizationEndpoint: `${KEYCLOAK_CONFIG.url}/realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/auth`,
        tokenEndpoint: `${KEYCLOAK_CONFIG.url}/realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/token`,
        revocationEndpoint: `${KEYCLOAK_CONFIG.url}/realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/revoke`,
        endSessionEndpoint: `${KEYCLOAK_CONFIG.url}/realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/logout`,
        userInfoEndpoint: `${KEYCLOAK_CONFIG.url}/realms/${KEYCLOAK_CONFIG.realm}/protocol/openid-connect/userinfo`,
    },
    clientId: KEYCLOAK_CONFIG.clientId,
};
