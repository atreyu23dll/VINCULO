import Constants from 'expo-constants';

// Extraemos la IP de la variable de entorno o usamos localhost por defecto
const API_URL = 'https://vinculo-1u39.onrender.com';

export const KEYCLOAK_CONFIG = {
    realm: 'Vinculo',
    clientId: 'vinculo-app',
    url: 'https://docosanoic-lightly-silva.ngrok-free.dev', 
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
