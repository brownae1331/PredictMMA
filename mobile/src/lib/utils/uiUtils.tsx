import React from 'react';
import { Platform, TouchableWithoutFeedback, Keyboard } from 'react-native';

export interface FormattedName {
    firstName: string;
    lastName: string;
}

export const formatFighterName = (fullName: string): FormattedName => {
    const nameParts = fullName.trim().split(' ');
    if (nameParts.length === 1) {
        return { firstName: nameParts[0], lastName: '' };
    }
    const firstName = nameParts[0];
    const lastName = nameParts.slice(1).join(' ');
    return { firstName, lastName };
};

export const DismissKeyboardView: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    if (Platform.OS === 'web') {
        return <>{children}</>;
    }
    return (
        <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
            {children}
        </TouchableWithoutFeedback>
    );
}; 